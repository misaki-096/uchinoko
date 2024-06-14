from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from ultralytics import YOLO
import tkinter as tk
from tkinter import filedialog
from PIL import Image, UnidentifiedImageError
import base64, mimetypes, uuid, glob, os
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

    def get(self, request, **kwargs):
        # 更新時にファイルダイアログが開かないようにトークンで判定
        request_token1 = self.request.GET.get("token1")
        session_token1 = self.request.session.pop("token1", "")
        if request_token1 == session_token1:
            file_name = Dialog.dialog(self, 0)

            if file_name != "":
                try:
                    yolo_result = YoloPredict.yolo_predict(self, file_name)

                    token1 = str(uuid.uuid4())
                    self.request.session["token1"] = token1
                    submit_token1 = self.request.session["token1"]

                    context = super().get_context_data(**kwargs)
                    return render(
                        request,
                        "app/home.html",
                        context={
                            "file_name": yolo_result[0],  # img_file,
                            "names": yolo_result[1],  # class_name,
                            "token1": submit_token1,
                            "keywords": context["keywords"],
                        },
                    )
                except UnidentifiedImageError:
                    messages.error(
                        request, "選択されたファイルを開くことができません。"
                    )
                    return redirect("app:home")

            else:
                return redirect("app:home")

        else:
            return redirect("app:home")


class ImageSearch(LoginRequiredMixin, TemplateView):
    template_name = "app/image_search.html"

    def get_context_data(self, **kwargs):

        sec_fetch_site = self.request.META["HTTP_SEC_FETCH_SITE"]
        if sec_fetch_site == "same-origin":
            context = super().get_context_data(**kwargs)

            user_id = self.request.user.id
            search_word = kwargs["search_word"]

            word_exists = Keyword.objects.filter(
                user_id=user_id, name__contains=search_word
            ).exists()
            if not word_exists:
                Keyword.objects.create(name=search_word, user_id=user_id)

            context["search_word"] = search_word

            return context

        else:
            return redirect("app:home")


class FolderChoice(ImageSearch):
    template_name = "app/image_search.html"

    def get(self, request, **kwargs):
        request_token2 = self.request.GET.get("token2")
        session_token2 = self.request.session.pop("token2", "")
        context = super().get_context_data(**kwargs)
        search_word = context["search_word"]

        if request_token2 == session_token2:
            files = Dialog.dialog(self, 1)

            if files != "no":
                try:
                    yolo_result = YoloPredict.yolo_predict(self, files, search_word)
                    res_len = len(yolo_result)
                    # for i in range(res_len):
                    # l = [d["url"] for d in yolo_result]

                except UnidentifiedImageError:
                    pass

                else:
                    token2 = str(uuid.uuid4())
                    self.request.session["token2"] = token2
                    submit_token2 = self.request.session["token2"]

                    return render(
                        request,
                        "app/image_search.html",
                        context={
                            "search_word": search_word,
                            "img_files": yolo_result,
                            "token2": submit_token2,
                            "img_num": res_len,
                        },
                    )

            return redirect("app:image_search", search_word)

        return redirect("app:image_search", search_word)


class Dialog:
    def dialog(self, c_num):
        root = tk.Tk()
        root.attributes("-topmost", True)
        root.withdraw()

        if c_num == 0:
            file_name = filedialog.askopenfilename(
                title="ファイルを開く",
                filetypes=[
                    ("画像ファイル", ".png .jpg"),
                    ("PNG", ".png"),
                    ("JPEG", ".jpg"),
                ],
            )
        elif c_num == 1:
            folder_name = filedialog.askdirectory(
                title="フォルダを開く", mustexist=True
            )
            if folder_name != "":
                file_name = glob.glob(
                    os.path.join(folder_name, "**/*." + (("jpg") or ("png"))),
                    recursive=True,
                )
            else:
                file_name = "no"

        root.destroy()
        return file_name


class YoloPredict:
    def yolo_predict(self, file_name, *args):
        model = YOLO("yolov8m.pt")
        if not args:
            results = model.predict(file_name, conf=0.5)
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

            with open(file_name, "rb") as f:
                b64_img = base64.b64encode(f.read())

            str_img = str(b64_img)
            img = str_img[2 : len(str_img) - 1]
            mimetype = mimetypes.guess_type(file_name)[0]
            img_file = f"data:{mimetype};base64,{img}"

            return img_file, class_name

        else:
            classes = model.names
            c = [key for key, value in classes.items() if value == args[0]]
            results = model.predict(file_name, conf=0.5, classes=c)

            d = []
            results_len = len(file_name)
            for i in range(results_len):
                result = results[i]
                if result:
                    with open(result.path, "rb") as f:
                        b64_img = base64.b64encode(f.read())

                    str_img = str(b64_img)
                    img = str_img[2 : len(str_img) - 1]
                    mimetype = mimetypes.guess_type(result.path)[0]
                    img_file = f"data:{mimetype};base64,{img}"

                    # d.append({"url": "aaa", "res": result.path})
                    d.append(img_file)

            return d  # img_file, class_name
