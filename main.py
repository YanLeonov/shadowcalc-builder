import math
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Ellipse
from kivy.utils import platform
from kivy.clock import Clock

if platform == 'android':
    from jnius import autoclass, cast, PythonJavaClass, java_method
    from android.permissions import request_permissions, Permission

class _GPSListener(PythonJavaClass):
    __javainterfaces__ = ['android/location/LocationListener']
    __javacontext__ = 'app'
    def __init__(self, on_fix):
        super(_GPSListener, self).__init__()
        self.on_fix = on_fix
    @java_method('(Landroid/location/Location;)V')
    def onLocationChanged(self, location):
        lat = location.getLatitude()
        lon = location.getLongitude()
        if self.on_fix:
            Clock.schedule_once(lambda dt: self.on_fix(lat, lon), 0)
    @java_method('(Ljava/lang/String;II)V')
    def onStatusChanged(self, provider, status, extras): pass
    @java_method('(Ljava/lang/String;)V')
    def onProviderEnabled(self, provider): pass
    @java_method('(Ljava/lang/String;)V')
    def onProviderDisabled(self, provider): pass

_gps_listener = None
_android_lm = None

def get_region_name(lat, lon):
    lat = round(lat, 2)
    lon = round(lon, 2)
    if -90 <= lat <= 90 and -180 <= lon <= 180:
        if 23.0 <= lat <= 50.0 and -125.0 <= lon <= -115.0: return "Калифорния (США)"
        elif 25.0 <= lat <= 50.0 and -105.0 <= lon <= -95.0: return "Техас (США)"
        elif 25.0 <= lat <= 50.0 and -90.0 <= lon <= -80.0: return "Флорида (США)"
        elif 15.0 <= lat <= 25.0 and -105.0 <= lon <= -90.0: return "Мексика"
        elif 7.0 <= lat <= 15.0 and -85.0 <= lon <= -75.0: return "Центральная Америка"
        elif -15.0 <= lat <= 7.0 and -85.0 <= lon <= -75.0: return "Колумбия"
        elif -5.0 <= lat <= 5.0 and -80.0 <= lon <= -70.0: return "Эквадор"
        elif -15.0 <= lat <= 0.0 and -75.0 <= lon <= -65.0: return "Перу"
        elif -25.0 <= lat <= -15.0 and -70.0 <= lon <= -60.0: return "Боливия"
        elif -30.0 <= lat <= -15.0 and -55.0 <= lon <= -40.0: return "Бразилия (юг)"
        elif -15.0 <= lat <= 5.0 and -60.0 <= lon <= -50.0: return "Бразилия (север)"
        elif -15.0 <= lat <= 5.0 and -35.0 <= lon <= -10.0: return "Южная Атлантика"
        elif -25.0 <= lat <= -15.0 and -10.0 <= lon <= 15.0: return "Южная Африка (Ангола)"
        elif -15.0 <= lat <= 0.0 and 8.0 <= lon <= 20.0: return "Центральная Африка (Конго)"
        elif 0.0 <= lat <= 15.0 and -5.0 <= lon <= 10.0: return "Западная Африка (Гвинея)"
        elif 10.0 <= lat <= 23.0 and 0.0 <= lon <= 15.0: return "Сахель (Чад)"
        elif 10.0 <= lat <= 23.0 and 30.0 <= lon <= 45.0: return "Судан"
        elif 0.0 <= lat <= 15.0 and 35.0 <= lon <= 50.0: return "Восточная Африка (Эфиопия)"
        elif 12.0 <= lat <= 25.0 and 42.0 <= lon <= 55.0: return "Йемен"
        elif 10.0 <= lat <= 25.0 and 55.0 <= lon <= 62.0: return "Оман"
        elif 5.0 <= lat <= 25.0 and 62.0 <= lon <= 78.0: return "Аравийское море"
        elif 5.0 <= lat <= 15.0 and 75.0 <= lon <= 85.0: return "Индия (юг)"
        elif 15.0 <= lat <= 25.0 and 72.0 <= lon <= 85.0: return "Индия (север)"
        elif 8.0 <= lat <= 25.0 and 85.0 <= lon <= 100.0: return "Бангладеш и Мьянма"
        elif 0.0 <= lat <= 15.0 and 95.0 <= lon <= 110.0: return "Индонезия (Суматра)"
        elif -10.0 <= lat <= 0.0 and 105.0 <= lon <= 120.0: return "Индонезия (Ява)"
        elif 10.0 <= lat <= 25.0 and 100.0 <= lon <= 110.0: return "Таиланд"
        elif 10.0 <= lat <= 20.0 and 105.0 <= lon <= 115.0: return "Вьетнам"
        elif 20.0 <= lat <= 30.0 and 110.0 <= lon <= 125.0: return "Южный Китай"
        elif 5.0 <= lat <= 20.0 and 120.0 <= lon <= 130.0: return "Филиппины"
        elif -15.0 <= lat <= -5.0 and 120.0 <= lon <= 145.0: return "Австралия (север)"
        elif -30.0 <= lat <= -15.0 and 145.0 <= lon <= 155.0: return "Австралия (восток)"
        elif -25.0 <= lat <= -15.0 and 110.0 <= lon <= 120.0: return "Австралия (запад)"
        elif -20.0 <= lat <= -5.0 and 45.0 <= lon <= 55.0: return "Мадагаскар"
        elif -25.0 <= lat <= -20.0 and 35.0 <= lon <= 45.0: return "Мозамбик"
        elif 35.0 <= lat <= 50.0 and 25.0 <= lon <= 40.0: return "Греция и Турция"
        elif 40.0 <= lat <= 55.0 and -10.0 <= lon <= 0.0: return "Испания и Португалия"
        elif 40.0 <= lat <= 50.0 and -5.0 <= lon <= 5.0: return "Франция"
        elif 50.0 <= lat <= 60.0 and -10.0 <= lon <= 5.0: return "Британия"
        elif 35.0 <= lat <= 50.0 and -80.0 <= lon <= -70.0: return "Восточное побережье США"
        elif 30.0 <= lat <= 45.0 and -125.0 <= lon <= -115.0: return "Западное побережье США"
        elif -55.0 <= lat <= -35.0 and -75.0 <= lon <= -65.0: return "Патагония (Чили)"
        elif -55.0 <= lat <= -35.0 and -70.0 <= lon <= -55.0: return "Аргентина"
        elif -30.0 <= lat <= -20.0 and 25.0 <= lon <= 35.0: return "Южная Африка (Зимбабве)"
        elif -35.0 <= lat <= -20.0 and 15.0 <= lon <= 30.0: return "Южная Африка (Намибия)"
        elif -35.0 <= lat <= -25.0 and 25.0 <= lon <= 35.0: return "ЮАР"
        elif 55.0 <= lat <= 70.0 and 30.0 <= lon <= 60.0: return "Северная Европа (Россия)"
        elif 45.0 <= lat <= 55.0 and 35.0 <= lon <= 55.0: return "Центральная Россия"
        elif 45.0 <= lat <= 60.0 and 55.0 <= lon <= 90.0: return "Урал и Западная Сибирь"
        elif 50.0 <= lat <= 75.0 and 70.0 <= lon <= 90.0: return "Нижневартовск (Сибирь)"
        elif 45.0 <= lat <= 60.0 and 90.0 <= lon <= 120.0: return "Восточная Сибирь"
        elif 40.0 <= lat <= 55.0 and 120.0 <= lon <= 145.0: return "Дальний Восток"
        elif 35.0 <= lat <= 45.0 and 135.0 <= lon <= 145.0: return "Япония"
        elif 50.0 <= lat <= 60.0 and -135.0 <= lon <= -125.0: return "Аляска"
        elif 40.0 <= lat <= 60.0 and -140.0 <= lon <= -120.0: return "Канада (запад)"
        elif 40.0 <= lat <= 55.0 and -100.0 <= lon <= -80.0: return "Центральная Канада"
        elif 40.0 <= lat <= 50.0 and -95.0 <= lon <= -85.0: return "Великие равнины США"
        elif -30.0 <= lat <= 10.0 and -180.0 <= lon <= -80.0: return "Тихий океан"
        elif -30.0 <= lat <= 10.0 and -80.0 <= lon <= -40.0: return "Южная Америка"
        elif -30.0 <= lat <= 10.0 and -40.0 <= lon <= -10.0: return "Атлантический океан"
        elif -30.0 <= lat <= 10.0 and -10.0 <= lon <= 40.0: return "Африка (центр)"
        elif -30.0 <= lat <= 10.0 and 40.0 <= lon <= 110.0: return "Индийский океан"
        elif -30.0 <= lat <= 10.0 and 110.0 <= lon <= 145.0: return "Юго-Восточная Азия"
        elif -30.0 <= lat <= 10.0 and 145.0 <= lon <= 180.0: return "Тихий океан (западная часть)"
        elif 10.0 <= lat <= 55.0 and -80.0 <= lon <= -10.0: return "Атлантический океан (север)"
        elif 10.0 <= lat <= 30.0 and -10.0 <= lon <= 50.0: return "Северная Африка"
        elif 10.0 <= lat <= 55.0 and 50.0 <= lon <= 100.0: return "Евразия (юг)"
        elif 30.0 <= lat <= 55.0 and -10.0 <= lon <= 50.0: return "Европа"
        elif 30.0 <= lat <= 55.0 and 100.0 <= lon <= 145.0: return "Китай и Корея"
        elif 30.0 <= lat <= 55.0 and -135.0 <= lon <= -100.0: return "Северная Америка (запад)"
        elif 30.0 <= lat <= 55.0 and -100.0 <= lon <= -70.0: return "Северная Америка (восток)"
        elif 55.0 <= lat <= 75.0 and -180.0 <= lon <= 180.0: return "Арктика"
        elif -90.0 <= lat <= -55.0 and -180.0 <= lon <= 180.0: return "Антарктида"
        elif 53.0 <= lat <= 56.0 and 35.0 <= lon <= 39.0: return "Москва и область"
        elif 55.0 <= lat <= 65.0 and 60.0 <= lon <= 70.0: return "Сибирь (ХМАО)"
        elif 40.0 <= lat <= 55.0 and 60.0 <= lon <= 75.0: return "Узбекистан"
        elif 45.0 <= lat <= 55.0 and 20.0 <= lon <= 30.0: return "Украина"
        elif 35.0 <= lat <= 50.0 and -120.0 <= lon <= -105.0: return "Запад США"
        elif 10.0 <= lat <= 18.0 and -90.0 <= lon <= -80.0: return "Карибское море"
        elif 0.0 <= lat <= 10.0 and -90.0 <= lon <= -75.0: return "Экваториальная Америка"
        elif 30.0 <= lat <= 38.0 and -15.0 <= lon <= 10.0: return "Средиземноморье"
        elif 5.0 <= lat <= 30.0 and 10.0 <= lon <= 30.0: return "Центральная Сахара"
        elif 30.0 <= lat <= 40.0 and 30.0 <= lon <= 45.0: return "Ближний Восток"
        elif 15.0 <= lat <= 27.0 and 45.0 <= lon <= 55.0: return "Центральная Аравия"
        elif 15.0 <= lat <= 28.0 and 65.0 <= lon <= 75.0: return "Пакистан"
        elif 30.0 <= lat <= 40.0 and 105.0 <= lon <= 120.0: return "Центральный Китай"
    return "Индийский океан"

class RoundYellowButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0,0,0,0)
        self.bind(pos=self.update_canvas, size=self.update_canvas)
    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1,0.9,0,1)
            s = min(self.width, self.height)
            Ellipse(pos=(self.x+(self.width-s)/2, self.y+(self.height-s)/2), size=(s,s))

class ShadowCalcApp(App):
    def build(self):
        self.title = 'ShadowCalc'
        self.my_lat, self.my_lon = 60.92, 76.60
        self.gps_fixed = False
        if platform == 'android':
            try: request_permissions([Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION])
            except: pass
        root = ScrollView(size_hint=(1,1))
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15, size_hint_y=None)
        main_layout.bind(minimum_height=main_layout.setter('height'))
        main_layout.add_widget(Label(text='== АВТО-ЗЕНИТ СОЛНЦА ==', font_size=38, bold=True, color=(1,0.9,0,1), size_hint_y=None, height=45))
        self.lbl_zenith_info = Label(text='Определение зенита...', font_size=34, bold=True, halign='center', size_hint_y=None, height=100)
        main_layout.add_widget(self.lbl_zenith_info)
        Clock.schedule_once(lambda dt: self.update_zenith(), 0.1)
        btn_container = BoxLayout(orientation='vertical', size_hint_y=None, height=260, padding=5)
        self.calc_btn = RoundYellowButton(text='РАСЧЁТ', font_size=42, bold=True, color=(0,0,0,1), halign='center')
        self.calc_btn.bind(on_press=self.on_calc)
        btn_container.add_widget(self.calc_btn)
        main_layout.add_widget(btn_container)
        self.txt_result = Label(text='Расстояние (D): Вычисление...\nВысота (H): Ожидание тени', font_size=36, bold=True, halign='center', size_hint_y=None, height=110)
        main_layout.add_widget(self.txt_result)
        main_layout.add_widget(Label(text='== ДАННЫЕ ИЗМЕРЯЛЬЩИКА ==', font_size=36, bold=True, color=(0.2,0.6,1,1), size_hint_y=None, height=45))
        self.lbl_loc = Label(text='GPS: Поиск...', font_size=32, bold=True, color=(0.2,1,0.2,1), halign='center', size_hint_y=None, height=85)
        main_layout.add_widget(self.lbl_loc)
        self.btn_manual = Button(text='Ввести координаты вручную', font_size=28, bold=True, background_color=(0.3,0.3,0.3,1), color=(1,1,1,1), size_hint_y=None, height=60)
        self.btn_manual.bind(on_press=self.toggle_manual)
        main_layout.add_widget(self.btn_manual)
        self.btn_retry = Button(text='Повторить поиск GPS', font_size=28, bold=True, background_color=(0,0.4,0.6,1), color=(1,1,1,1), size_hint_y=None, height=55)
        self.btn_retry.bind(on_press=lambda x: self.retry_gps())
        main_layout.add_widget(self.btn_retry)
        self.manual_box = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=70)
        self.manual_lat = TextInput(text='', hint_text='Широта', multiline=False, font_size=28, input_filter='float', size_hint_x=0.5)
        self.manual_lon = TextInput(text='', hint_text='Долгота', multiline=False, font_size=28, input_filter='float', size_hint_x=0.5)
        self.btn_apply = Button(text='Применить', font_size=24, bold=True, size_hint_x=0.3, background_color=(0,0.5,0,1), color=(1,1,1,1))
        self.btn_apply.bind(on_press=self.apply_manual)
        self.manual_box.add_widget(self.manual_lat)
        self.manual_box.add_widget(self.manual_lon)
        self.manual_box.add_widget(self.btn_apply)
        self.manual_box.opacity = 0
        self.manual_box.disabled = True
        main_layout.add_widget(self.manual_box)
        pole = BoxLayout(orientation='horizontal', spacing=15, size_hint_y=None, height=75)
        self.btn_std = ToggleButton(text='Стандарт (1 м)', state='down', group='pole', font_size=30, bold=True)
        self.btn_custom = ToggleButton(text='Свой шест', state='normal', group='pole', font_size=30, bold=True)
        self.btn_std.bind(on_press=self.toggle_pole)
        self.btn_custom.bind(on_press=self.toggle_pole)
        pole.add_widget(self.btn_std)
        pole.add_widget(self.btn_custom)
        main_layout.add_widget(pole)
        self.h_input = TextInput(text='1.0', multiline=False, disabled=True, font_size=42, input_filter='float', size_hint_y=None, height=85)
        main_layout.add_widget(self.h_input)
        main_layout.add_widget(Label(text='Впиши длину тени от шеста:', font_size=36, bold=True, size_hint_y=None, height=45))
        self.l_input = TextInput(text='', multiline=False, font_size=42, input_filter='float', size_hint_y=None, height=85)
        main_layout.add_widget(self.l_input)
        root.add_widget(main_layout)
        Clock.schedule_once(lambda dt: self.start_gps(), 0.5)
        return root

    def toggle_pole(self, inst):
        if self.btn_custom.state == 'down':
            self.h_input.disabled = False
            self.h_input.text = ''
        else:
            self.h_input.text = '1.0'
            self.h_input.disabled = True

    def toggle_manual(self, inst):
        if self.manual_box.opacity == 0:
            self.manual_box.opacity = 1
            self.manual_box.disabled = False
            self.manual_lat.text = str(self.my_lat)
            self.manual_lon.text = str(self.my_lon)
        else:
            self.manual_box.opacity = 0
            self.manual_box.disabled = True

    def apply_manual(self, inst):
        try:
            lat = float(self.manual_lat.text)
            lon = float(self.manual_lon.text)
            if -90<=lat<=90 and -180<=lon<=180:
                self.my_lat = lat
                self.my_lon = lon
                self.gps_fixed = True
                self.lbl_loc.text = f'GPS: Ручной ввод\n({lat:.4f}°, {lon:.4f}°)'
                self.lbl_loc.color = (1,0.8,0,1)
                self.calc()
        except: pass

    def start_gps(self):
        if platform!='android' or self.gps_fixed: return
        global _gps_listener, _android_lm
        self.lbl_loc.text = 'GPS: Поиск...'
        try:
            Context = autoclass('android.content.Context')
            Looper = autoclass('android.os.Looper')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            lm = PythonActivity.mActivity.getSystemService(Context.LOCATION_SERVICE)
            _android_lm = cast('android.location.LocationManager', lm)
            last = _android_lm.getLastKnownLocation('gps')
            if last is None: last = _android_lm.getLastKnownLocation('network')
            if last and (last.getLatitude()!=0 or last.getLongitude()!=0):
                self.got_fix(last.getLatitude(), last.getLongitude())
                return
            if _gps_listener is None:
                _gps_listener = _GPSListener(self.got_fix)
            _android_lm.requestLocationUpdates('gps', 2000, 0, _gps_listener, Looper.getMainLooper())
        except:
            self.lbl_loc.text = 'GPS: Ошибка'
            self.lbl_loc.color = (1,0.3,0.3,1)

    def got_fix(self, lat, lon):
        self.my_lat, self.my_lon = lat, lon
        self.gps_fixed = True
        self.lbl_loc.text = f'GPS: Получены\n({lat:.4f}°, {lon:.4f}°)'
        self.lbl_loc.color = (0.2,1,0.2,1)
        self.calc()

    def retry_gps(self):
        global _android_lm, _gps_listener
        self.gps_fixed = False
        if platform=='android' and _android_lm and _gps_listener:
            try: _android_lm.removeUpdates(_gps_listener)
            except: pass
        Clock.schedule_once(lambda dt: self.start_gps(), 0.3)

    def update_zenith(self):
        from datetime import timezone
        n = datetime.now(timezone.utc)
        day = n.timetuple().tm_yday
        zl = 23.45 * math.sin(math.radians(360/365*(284+day)))
        zh = 15.0*(12.0 - (n.hour + n.minute/60.0))
        if zh>180: zh-=360
        elif zh<-180: zh+=360
        self.zen_lat, self.zen_lon = zl, zh
        self.lbl_zenith_info.text = f'Зенит над: {get_region_name(zl,zh)}\n({zl:.2f}°, {zh:.2f}°)'

    def on_calc(self, inst):
        self.update_zenith()
        self.calc()

    def calc(self):
        try:
            if not hasattr(self,'zen_lat'): self.update_zenith()
            D = 111.32*((self.my_lat-self.zen_lat)**2 + (self.my_lon-self.zen_lon)**2)**0.5
            h = float(self.h_input.text or 0)
            L = float(self.l_input.text or 0)
            if h<=0 or L<=0:
                self.txt_result.text = f'Расстояние (D): {D:.1f} км\nВведите тень и нажмите РАСЧЁТ'
                return
            H = D*h/L
            self.calc_btn.text = f'{H:.0f}\nкм'
            self.txt_result.text = f'Расстояние (D): {D:.1f} км\nВысота Солнца (H): {H:.1f} км'
        except:
            self.txt_result.text = 'Ошибка расчёта'

if __name__ == '__main__':
    ShadowCalcApp().run()
