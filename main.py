import os
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import AsyncImage
from kivy.properties import StringProperty, NumericProperty
from kivy.clock import Clock
from kivy.utils import platform
from kivy.core.window import Window

# बैकग्राउंड को डार्क थीम देने के लिए
Window.clearcolor = (0.08, 0.08, 0.08, 1)

KV = '''
<GalleryImage>:
    allow_stretch: True
    keep_ratio: True
    mipmap: True
    canvas.before:
        Color:
            rgba: 0.16, 0.16, 0.16, 1
        Rectangle:
            pos: self.pos
            size: self.size

<ImagePreviewModal>:
    size_hint: 1, 1
    background_color: 0, 0, 0, 0.95
    auto_dismiss: False

    BoxLayout:
        orientation: 'vertical'

        # Top Action Bar
        BoxLayout:
            size_hint_y: None
            height: '56dp'
            padding: '10dp'
            spacing: '10dp'
            canvas.before:
                Color:
                    rgba: 0.12, 0.12, 0.12, 1
                Rectangle:
                    pos: self.pos
                    size: self.size

            Label:
                text: root.image_name
                color: 1, 1, 1, 1
                font_size: '15sp'
                halign: 'left'
                valign: 'middle'
                text_size: self.size
                shorten: True
                shorten_from: 'right'

            Button:
                text: 'Close'
                size_hint_x: None
                width: '80dp'
                background_normal: ''
                background_color: 0.85, 0.2, 0.2, 1
                bold: True
                on_release: root.dismiss()

        # Pinch-to-Zoom एरिया
        RelativeLayout:
            Scatter:
                do_rotation: False
                do_translation: True
                do_scale: True
                min_scale: 1.0
                max_scale: 4.0
                size_hint: None, None
                size: self.parent.size

                AsyncImage:
                    source: root.image_source
                    size: self.parent.size
                    allow_stretch: True
                    keep_ratio: True

<GalleryScreen>:
    orientation: 'vertical'

    # Header Bar
    BoxLayout:
        size_hint_y: None
        height: '60dp'
        padding: '15dp', '10dp'
        spacing: '10dp'
        canvas.before:
            Color:
                rgba: 0.14, 0.14, 0.14, 1
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: f"My Gallery ({root.total_images} Photos)"
            font_size: '18sp'
            bold: True
            color: 1, 1, 1, 1
            halign: 'left'
            valign: 'middle'
            text_size: self.size

        Button:
            text: 'Refresh'
            size_hint_x: None
            width: '90dp'
            background_normal: ''
            background_color: 0.2, 0.5, 0.9, 1
            bold: True
            on_release: app.check_permissions_and_load()

    # Status Label (जब कोई फोटो न मिले)
    Label:
        id: status_label
        text: root.status_text
        size_hint_y: None
        height: '40dp' if root.status_text else '0dp'
        opacity: 1 if root.status_text else 0
        color: 0.75, 0.75, 0.75, 1
        font_size: '14sp'

    # High-Performance RecycleView Grid
    RecycleView:
        id: rv
        viewclass: 'GalleryImage'
        scroll_type: ['bars', 'content']
        bar_width: '6dp'
        bar_color: 0.3, 0.6, 1, 0.8

        RecycleGridLayout:
            cols: 3
            spacing: '6dp'
            padding: '6dp'
            default_size: None, dp(130)
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
'''

Builder.load_string(KV)


class GalleryImage(ButtonBehavior, AsyncImage):
    """गैलरी का थंबनेल जिस पर क्लिक करने से फुल-स्क्रीन फोटो खुलेगी"""
    def on_release(self):
        if self.source:
            modal = ImagePreviewModal(
                image_source=self.source,
                image_name=os.path.basename(self.source)
            )
            modal.open()


class ImagePreviewModal(ModalView):
    """फुल-स्क्रीन इमेज और ज़ूम पॉपअप"""
    image_source = StringProperty("")
    image_name = StringProperty("")


class GalleryScreen(BoxLayout):
    total_images = NumericProperty(0)
    status_text = StringProperty("Loading photos...")


class GalleryApp(App):
    def build(self):
        self.title = "Pro Gallery"
        self.screen = GalleryScreen()
        # ऐप स्टार्ट होते ही परमिशन और फोटो लोड शुरू करें
        Clock.schedule_once(lambda dt: self.check_permissions_and_load(), 0.2)
        return self.screen

    def check_permissions_and_load(self):
        """Android होने पर Runtime Permission मांगेगा, वरना सीधे लोड करेगा"""
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                permissions = [
                    Permission.READ_EXTERNAL_STORAGE,
                    "android.permission.READ_MEDIA_IMAGES"  # Android 13+ के लिए
                ]
                request_permissions(permissions, self.on_permission_Result)
            except Exception:
                self.load_images()
        else:
            self.load_images()

    def on_permission_Result(self, permissions, grants):
        # Permission रिस्पॉन्स आने के बाद मेन थ्रेड पर इमेज लोड करें
        Clock.schedule_once(lambda dt: self.load_images(), 0.1)

    def get_image_directories(self):
        """Android और PC दोनों के संभावित इमेज फोल्डर्स की लिस्ट"""
        dirs = []
        if platform == 'android':
            base_paths = ['/storage/emulated/0', '/sdcard']
            sub_folders = [
                'DCIM/Camera',
                'DCIM/Screenshots',
                'Pictures',
                'Download',
                'WhatsApp/Media/WhatsApp Images'
            ]
            for base in base_paths:
                if os.path.exists(base):
                    for sub in sub_folders:
                        full_path = os.path.join(base, sub)
                        if os.path.exists(full_path):
                            dirs.append(full_path)
                    break  # डुप्लीकेट स्कैन से बचने के लिए एक ही बेस पाथ लें
        else:
            # PC / Laptop पर टेस्टिंग के लिए
            home = os.path.expanduser('~')
            for sub in ['Pictures', 'Downloads', 'Desktop']:
                full_path = os.path.join(home, sub)
                if os.path.exists(full_path):
                    dirs.append(full_path)
        return dirs

    def load_images(self):
        valid_extensions = ('.png', '.jpg', '.jpeg', '.webp')
        found_images = []
        seen_paths = set()

        for folder in self.get_image_directories():
            try:
                for file in os.listdir(folder):
                    if file.lower().endswith(valid_extensions) and not file.startswith('.'):
                        full_path = os.path.realpath(os.path.join(folder, file))
                        if full_path not in seen_paths:
                            seen_paths.add(full_path)
                            try:
                                mtime = os.path.getmtime(full_path)
                            except OSError:
                                mtime = 0
                            found_images.append((mtime, full_path))
            except PermissionError:
                continue
            except Exception:
                continue

        # सबसे नई फोटोज़ को सबसे पहले रखने के लिए सॉर्ट करें
        found_images.sort(key=lambda x: x[0], reverse=True)

        # RecycleView में डेटा अपडेट करें
        self.screen.ids.rv.data = [{'source': img_path} for _, img_path in found_images]
        self.screen.total_images = len(found_images)

        if found_images:
            self.screen.status_text = ""
        else:
            self.screen.status_text = "No images found or Storage Permission not granted."


if __name__ == '__main__':
    GalleryApp().run()
