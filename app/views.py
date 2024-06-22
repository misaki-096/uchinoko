import base64
import glob
import json
import os
import pathlib
import shutil
import tkinter as tk
import uuid
from tkinter import filedialog

import requests
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, TemplateView, View
from ultralytics import YOLO

from .models import Keyword


class Home(LoginRequiredMixin, TemplateView):
    template_name = "app/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = self.request.user.id
        keywords = Keyword.objects.filter(user_id=user_id).order_by("-name")
        context["keywords"] = keywords
        return context


class Image(Home):
    template_name = "app/home.html"

    def post(self, request):
        self.request.session["token"] = "token"
        return redirect("app:image")

    def get(self, request, **kwargs):
        if "token" in self.request.session:
            del self.request.session["token"]

            file_name = Dialog.dialog(self, 0)

            if file_name != "":
                try:
                    yolo_result = YoloPredict.yolo_predict(self, file_name)

                except Exception:
                    messages.error(
                        request, "選択されたファイルを開くことができません。"
                    )
                    return redirect("app:home")

                else:
                    context = super().get_context_data(**kwargs)
                    return render(
                        request,
                        "app/home.html",
                        context={
                            "file_url": yolo_result[0],  # img_file
                            "names": yolo_result[1],  # class_name
                            "keywords": context["keywords"],
                            "file_name": file_name,
                        },
                    )

        return redirect("app:home")


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

        if folder != "no":
            if "param" in j_request:  # search_wordにあてはまる画像をフォルダ内から探す
                search_word = j_request["param"]

                try:
                    yolo_result = YoloPredict.yolo_predict(self, folder, search_word)
                    # l = [d["url"] for d in yolo_result]

                except FileNotFoundError:
                    return JsonResponse({"folder": folder, "img_files": "no_files"})

                else:
                    return JsonResponse(
                        {
                            "folder": folder,
                            "img_files": yolo_result,
                        }
                    )

            else:  # チェックがある画像を選択したフォルダに移動させる
                values = [d.get("check") for d in j_request]
                move_file = []
                for value in values:
                    p = value.replace(os.sep, "/")
                    dirname = os.path.dirname(p)
                    if dirname != folder:
                        shutil.move(value, folder)
                        move_file.append("ok")
                    else:
                        move_file.append("exists")

                return JsonResponse(
                    {"folder": folder, "move_file": move_file}, safe=False
                )

        else:
            return JsonResponse({"folder": "no"})


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
            folder_name = filedialog.askdirectory(
                title="フォルダを開く", mustexist=True
            )
            if folder_name != "":
                f_name = folder_name
            else:
                f_name = "no"

        root.destroy()
        return f_name


class YoloPredict:
    def yolo_predict(self, f_name, *args):
        model = YOLO("yolov8l.pt")
        if not args:  # Imageからの処理（1枚の画像の物体検出）
            results = model.predict(source=f_name, conf=0.5)
            result = results[0]
            item = len(result.boxes)
            if item != 0:
                class_ids = result.boxes.cls
                name_dict = result.names
                class_name = []
                for class_id in class_ids:
                    class_name.append(name_dict[int(class_id)])

            else:
                class_name = "no"

            img_file = YoloPredict.url_b64(self, f_name)
            return img_file, class_name

        else:  # Searchからの処理（clsにあてはまる画像を探す）
            classes = model.names
            cls = [key for key, value in classes.items() if value == args[0]]

            results = model.predict(
                source=f"{f_name}/**/*.jpg",
                stream=True,
                # imgsz=1088,
                conf=0.5,
                classes=cls,
            )

            d = []
            for result in results:
                if result:
                    img_file = YoloPredict.url_b64(self, result.path)
                    d.append({"url": img_file, "file_path": result.path})

            return d

    def url_b64(self, file):
        with open(file, "rb") as f:
            b64_img = base64.b64encode(f.read())

        str_img = str(b64_img)
        img = str_img[2 : len(str_img) - 1]
        img_file = f"data:image/jpeg;base64,{img}"

        return img_file
