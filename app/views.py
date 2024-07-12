import base64
import json
import os
import shutil
import tkinter as tk
from tkinter import filedialog

import cv2
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DeleteView, TemplateView
from ultralytics import YOLO
from ultralytics.utils.plotting import Colors

from .models import Keyword


class Home(LoginRequiredMixin, TemplateView):
    template_name = "app/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        search_words = Keyword.objects.filter(user_id=user_id).order_by("id")
        context["search_words"] = search_words
        return context


class ImageFile(Home):
    def get(self, request):
        file_name = Dialog.dialog(self, 0)

        if file_name != "":
            try:
                yolo_result = YoloPredict.yolo_predict(self, file_name)

            except cv2.error:
                return JsonResponse(
                    {
                        "file": file_name,
                        "error": "error",
                    }
                )

            else:
                return JsonResponse(
                    {
                        "file": file_name,
                        "file_url": yolo_result[0],  # img_file
                        "names": yolo_result[1],  # class_name
                    }
                )

        return JsonResponse({"file": ""})


class Search(LoginRequiredMixin, TemplateView):
    template_name = "app/search.html"

    def get(self, request):
        sec_fetch_site = self.request.META["HTTP_SEC_FETCH_SITE"]
        if sec_fetch_site == "same-origin":
            user_id = self.request.user.id
            search_word = self.request.GET.get("search_word")

            word_exists = Keyword.objects.filter(
                user_id=user_id, name__contains=search_word
            ).exists()

            if not word_exists:
                Keyword.objects.create(name=search_word, user_id=user_id)

            return render(
                request, "app/search.html", context={"search_word": search_word}
            )

        else:
            return redirect("app:home")

    def post(self, request):
        j_request = json.loads(self.request.body)
        folder = Dialog.dialog(self, 1)

        if folder != "":
            if "param" in j_request:  # search_wordにあてはまる画像をフォルダ内から探す
                search_word = j_request["param"]
                yolo = j_request["yolo"]

                try:
                    yolo_result = YoloPredict.predict_cls(
                        self, folder, search_word, yolo
                    )

                except FileNotFoundError:
                    return JsonResponse({"folder": folder, "img_files": "no_files"})

                else:
                    return JsonResponse(
                        {
                            "folder": folder,
                            "img_files": yolo_result,
                        },
                    )

            else:  # チェックがある画像を選択したフォルダに移動させる
                values = [d.get("check") for d in j_request]
                move_files = []
                for value in values:
                    p = value.replace(os.sep, "/")
                    dirname = os.path.dirname(p)
                    if dirname != folder:
                        shutil.move(value, folder)
                        move_files.append("ok")
                    else:
                        move_files.append("exists")

                return JsonResponse({"folder": folder, "move_files": move_files})

        else:
            return JsonResponse({"folder": ""})


class Dialog:
    def dialog(self, num):
        root = tk.Tk()
        root.attributes("-topmost", True)
        root.withdraw()

        if num == 0:
            f_name = filedialog.askopenfilename(
                title="ファイルを開く",
                filetypes=[
                    ("画像ファイル", ".jpg"),
                    ("JPEG", ".jpg"),
                ],
            )
        elif num == 1:
            f_name = filedialog.askdirectory(title="フォルダを開く", mustexist=True)

        root.destroy()
        return f_name


class YoloPredict:
    def yolo_predict(self, file_name):
        model = YOLO("yolov8l.pt")

        # Imageからの処理（1枚の画像の物体検出）
        results = model.predict(source=file_name, conf=0.3)
        result = results[0]
        item = len(result.boxes)
        if item != 0:
            class_ids = result.boxes.cls
            name_dict = result.names
            boxes_xy = result.boxes.xyxy
            boxes_wh = result.boxes.xywh

            class_name = []
            for class_id, box_xy, box_wh in zip(class_ids, boxes_xy, boxes_wh):
                c = Colors()
                color = c(class_id)
                class_name.append(
                    {
                        "name": name_dict[int(class_id)],
                        "box": [
                            int(i) for i in box_xy[:2]
                        ]  # バウンディングボックスの「左上の位置」を取得
                        + [
                            int(i) for i in box_wh[2:]
                        ],  # バウンディングボックスの「縦横の長さ」を取得
                        "color": color,
                    }
                )

        else:
            class_name = "no"

        img_file = YoloPredict.url_b64(self, file_name)
        return img_file, class_name

    def predict_cls(self, folder_name, *args):
        if args[1] == "yolo_n":
            model = YOLO("yolov8n.pt")
        else:
            model = YOLO("yolov8l.pt")

        # Searchからの処理（clsにあてはまる画像を探す）
        classes = model.names
        cls = [key for key, value in classes.items() if value == args[0]]

        results = model.predict(
            source=f"{folder_name}/**/*.jpg",
            stream=True,
            conf=0.3,
            iou=0.4,
            classes=cls,
        )

        d = []
        try:
            for result in results:
                if result:
                    img_file = YoloPredict.url_b64(self, result.path)
                    d.append({"url": img_file, "file_path": result.path})

        except FileNotFoundError as e:
            raise e  # ファイルが無い場合はエラーを送る

        except cv2.error:
            # ファイルはあるが破損などで開かない場合はメッセージを送る
            d.append(
                {
                    "error": "処理の途中でエラーが発生しました。開くことが出来ないファイルがあります。",
                }
            )

        return d

    def url_b64(self, file):
        with open(file, "rb") as f:
            b64_img = base64.b64encode(f.read())

        str_img = str(b64_img)
        img = str_img[2 : len(str_img) - 1]
        img_file = f"data:image/jpeg;base64,{img}"

        return img_file


class WordDelete(DeleteView):
    model = Keyword
    success_url = reverse_lazy("app:home")
