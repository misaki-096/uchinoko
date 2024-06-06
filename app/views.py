from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from ultralytics import YOLO
import tkinter as tk
from tkinter import filedialog
from PIL import Image
import os
import io
import requests
import base64, mimetypes, uuid


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "app/home.html"


class ImageView(LoginRequiredMixin, View):
    def dialog(self):
        root = tk.Tk()
        root.geometry("0x0")
        root.overrideredirect(1)

        file_name = filedialog.askopenfilename(
            title="ファイルを開く",
            filetypes=[
                ("画像ファイル", ".png .jpg"),
                ("PNG", ".png"),
                ("JPEG", ".jpg"),
            ],
        )

        root.destroy()
        return file_name

    def get(self, request):
        # 更新時にファイルダイアログが開かないようにトークンで判定
        request_token = self.request.GET.get("token")
        session_token = self.request.session.pop("token", "")
        if request_token == session_token:
            file_name = self.dialog()

            if file_name != "":
                model = YOLO("yolov8m.pt")
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

                token = str(uuid.uuid4())
                self.request.session["token"] = token
                submit_token = self.request.session["token"]

                return render(
                    request,
                    "app/home.html",
                    context={
                        "file_name": img_file,
                        "names": class_name,
                        "token": submit_token,
                    },
                )

            else:
                return redirect("app:home")

        else:
            return redirect("app:home")


class ImagesListView(View):
    template_name = "app/images_list.html"
