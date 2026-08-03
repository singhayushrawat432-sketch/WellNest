import kivy
from kivy.app import App
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from database import Database
from datetime import datetime

class SplashScreen(Screen):
    def on_enter(self):
        self.ids.loading_label.opacity = 1
        self.ids.progress_bar.value = 0
        self._loading_dot_index = 0

        anim = Animation(opacity=1, duration=0.8) + Animation(opacity=0.2, duration=0.8)
        anim.repeat = True
        anim.start(self.ids.loading_label)
        self.loading_anim = anim

        Animation(value=100, duration=1.5).start(self.ids.progress_bar)
        self.loading_clock = Clock.schedule_interval(self.update_loading_text, 0.4)
        Clock.schedule_once(self.go_next, 1.5)

    def update_loading_text(self, dt):
        self._loading_dot_index = (self._loading_dot_index + 1) % 4
        dots = '.' * self._loading_dot_index
        self.ids.loading_label.text = f'Loading{dots}'

    def go_next(self, dt):
        if hasattr(self, 'loading_anim'):
            self.loading_anim.stop(self.ids.loading_label)
        if hasattr(self, 'loading_clock'):
            self.loading_clock.cancel()
        self.manager.current = 'login'

class LoginScreen(Screen):
    
    def login(self):
        app = App.get_running_app()
        username = self.ids.username_input.text.strip()
        email = self.ids.email_input.text.strip()
        password = self.ids.password_input.text
        if app.db.login(username, email, password):
            user = app.db.get_user()
            if user:
                app.current_user = user[2] or username or email
            self.manager.current = 'home'
        else:
            self.ids.error_label.text = 'Invalid login credentials'

    def go_register(self):
        self.manager.current = 'register'

class RegisterScreen(Screen):
    def register(self):
        app = App.get_running_app()
        username = self.ids.register_username.text.strip()
        email = self.ids.register_email.text.strip()
        password = self.ids.register_password.text
        if username and email and password:
            if app.db.get_user():
                self.ids.register_error.text = 'Account already exists.'
                return
            app.db.create_user(username, email, password)
            self.manager.current = 'login'
        else:
            self.ids.register_error.text = 'Please fill all fields'

class ProfileScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        user = app.db.get_user()
        if user:
            self.ids.name_input.text = user[1] or ''
            self.ids.username_input.text = user[2] or ''
            self.ids.email_input.text = user[3] or ''
            # Don't load password for security

    def save_profile(self):
        app = App.get_running_app()
        name = self.ids.name_input.text.strip()
        username = self.ids.username_input.text.strip()
        email = self.ids.email_input.text.strip()
        password = self.ids.password_input.text
        if username and email:
            if password:
                app.db.update_user(name or username, username, email, password)
            else:
                app.db.update_user(name or username, username, email)
            app.current_user = username or email
            self.manager.current = 'home'
        else:
            self.ids.error_label.text = 'Please fill username and email'

class HomeScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        user = app.db.get_user()
        username = app.current_user or (user[2] if user and user[2] else 'User')
        self.ids.welcome_label.text = f'Welcome, {username}!'
        today = datetime.now().strftime('%Y-%m-%d')
        checkin = app.db.get_checkin(today)
        if checkin:
            self.ids.reminder_label.text = 'Great! You\'ve checked in today.'
        else:
            self.ids.reminder_label.text = 'Reminder: Don\'t forget your daily check-in!'

class CheckInScreen(Screen):
    def submit_checkin(self):
        app = App.get_running_app()
        mood_text = self.ids.mood_spinner.text
        stress_text = self.ids.stress_spinner.text
        sleep_text = self.ids.sleep_spinner.text
        notes = self.ids.notes_input.text
        
        mood_map = {'😢 Very Bad': 1, '😕 Bad': 2, '😐 Okay': 5, '🙂 Good': 8, '😊 Great': 10}
        stress_map = {'Low': 1, 'Medium': 5, 'High': 9}
        sleep_map = {'Good': 8, 'Average': 5, 'Poor': 2}
        
        mood = mood_map.get(mood_text, 5)
        anxiety = stress_map.get(stress_text, 5)
        sleep_hours = float(sleep_map.get(sleep_text, 5))
        
        date = datetime.now().strftime('%Y-%m-%d')
        app.db.add_checkin(date, mood, anxiety, sleep_hours, '', notes)
        self.manager.current = 'home'

class SupportCircleScreen(Screen):
    def on_enter(self):
        self.load_contacts()
        self.load_messages()
        if 'friend_update_input' in self.ids:
            self.ids.friend_update_input.text = ''
        if 'friend_status' in self.ids:
            self.ids.friend_status.text = ''

    def load_contacts(self):
        app = App.get_running_app()
        self.ids.circle_grid.clear_widgets()
        contacts = app.db.get_support_contacts()
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        if not contacts:
            self.ids.circle_grid.add_widget(Label(text='No trusted friends added yet.', size_hint_y=None, height=40))
            return
        for contact in contacts:
            contact_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=120, spacing=10)
            text = (
                f"{contact[1]} ({contact[2] or 'Trusted Friend'})\n"
                f"Phone: {contact[3]}\n"
                f"Email: {contact[4] or 'N/A'}\n"
                f"Notes: {contact[5] or 'None'}"
            )
            contact_box.add_widget(Label(text=text, text_size=(self.width * 0.65, None), size_hint_x=0.75))
            connect_button = Button(text='Connect', size_hint_x=0.25)
            connect_button.bind(on_press=lambda btn, name=contact[1], phone=contact[3]: self.connect_friend(name, phone))
            contact_box.add_widget(connect_button)
            self.ids.circle_grid.add_widget(contact_box)

    def save_contact(self):
        app = App.get_running_app()
        name = self.ids.contact_name.text.strip()
        relationship = self.ids.contact_relation.text.strip()
        phone = self.ids.contact_phone.text.strip()
        email = self.ids.contact_email.text.strip()
        notes = self.ids.contact_notes.text.strip()
        if not name or not phone:
            self.ids.friend_status.text = 'Name and phone are required.'
            return
        app.db.add_support_contact(name, relationship or 'Trusted Friend', phone, email, notes)
        self.ids.contact_name.text = ''
        self.ids.contact_relation.text = ''
        self.ids.contact_phone.text = ''
        self.ids.contact_email.text = ''
        self.ids.contact_notes.text = ''
        self.ids.friend_status.text = 'Trusted friend added.'
        self.load_contacts()

    def connect_friend(self, name, phone):
        if hasattr(self.ids, 'friend_status'):
            self.ids.friend_status.text = f'Connecting with {name}... use phone {phone} to reach out.'

    def share_update(self):
        app = App.get_running_app()
        message = self.ids.friend_update_input.text.strip()
        if not message:
            self.ids.friend_status.text = 'Please enter an update to share.'
            return
        app.db.add_support_message('Support Circle', message)
        self.ids.friend_update_input.text = ''
        self.ids.friend_status.text = 'Update shared with your trusted friends.'
        self.load_messages()

    def load_messages(self):
        if 'message_grid' not in self.ids:
            return
        app = App.get_running_app()
        self.ids.message_grid.clear_widgets()
        messages = app.db.get_support_messages()
        from kivy.uix.label import Label
        if not messages:
            self.ids.message_grid.add_widget(Label(text='No shared updates yet.', size_hint_y=None, height=40))
            return
        for name, message, timestamp in messages:
            self.ids.message_grid.add_widget(Label(text=f'[{timestamp}] {message}', text_size=(self.width - 40, None), size_hint_y=None, height=60))

class HistoryScreen(Screen):
    def on_enter(self):
        self.load_history()

    def load_history(self):
        app = App.get_running_app()
        self.ids.history_grid.clear_widgets()
        checkins = app.db.get_all_checkins()
        from kivy.uix.label import Label
        if not checkins:
            self.ids.history_grid.add_widget(Label(text='No check-in history yet.', size_hint_y=None, height=40))
            return
        for checkin in checkins:
            text = f"Date: {checkin[1]}\nMood: {checkin[2]}\nAnxiety: {checkin[3]}\nSleep: {checkin[4]}h\nActivities: {checkin[5]}\nNotes: {checkin[6]}"
            self.ids.history_grid.add_widget(Label(text=text, size_hint_y=None, height=100))

class WeeklyReportScreen(Screen):
    def on_enter(self):
        self.load_weekly_report()

    def load_weekly_report(self):
        app = App.get_running_app()
        self.ids.weekly_grid.clear_widgets()
        checkins = app.db.get_checkins_last_n_days(7)
        from kivy.uix.label import Label
        if not checkins:
            self.ids.weekly_grid.add_widget(Label(text='No weekly data yet.', size_hint_y=None, height=40))
            return
        
        moods = [row[2] for row in checkins]
        anxieties = [row[3] for row in checkins]
        sleep = [row[4] for row in checkins if row[4] is not None]
        avg_mood = sum(moods) / len(moods)
        avg_anxiety = sum(anxieties) / len(anxieties)
        avg_sleep = sum(sleep) / len(sleep) if sleep else 0.0
        
        # Summary
        summary_text = (
            f"Weekly Insights ({len(checkins)} entries)\n"
            f"Avg mood: {avg_mood:.1f}/10 | Avg stress: {avg_anxiety:.1f}/9 | Avg sleep: {avg_sleep:.1f}h"
        )
        self.ids.weekly_grid.add_widget(Label(text=summary_text, size_hint_y=None, height=80))
        
        # Mood trend graph visualization
        mood_graph = self._build_mood_graph(moods)
        self.ids.weekly_grid.add_widget(Label(text='Mood Trend:\n' + mood_graph, size_hint_y=None, height=120))
        
        # Stress trend visualization
        stress_trend = self._build_stress_trend(anxieties)
        self.ids.weekly_grid.add_widget(Label(text='Stress Trend:\n' + stress_trend, size_hint_y=None, height=60))
        
        # Mood history list
        self.ids.weekly_grid.add_widget(Label(text='Mood History:', size_hint_y=None, height=30))
        for checkin in reversed(checkins):
            mood_emoji = self._mood_emoji(checkin[2])
            text = f"{checkin[1]}: {mood_emoji} Mood {checkin[2]}/10 | Stress {checkin[3]}/9"
            self.ids.weekly_grid.add_widget(Label(text=text, size_hint_y=None, height=40))
    
    def _mood_emoji(self, mood):
        if mood <= 2:
            return '😢'
        elif mood <= 4:
            return '😕'
        elif mood <= 6:
            return '😐'
        elif mood <= 8:
            return '🙂'
        else:
            return '😊'
    
    def _build_mood_graph(self, moods):
        if not moods:
            return ''
        max_mood = max(moods) if moods else 10
        graph_lines = []
        for level in range(10, 0, -1):
            line = f'{level:2d} |'
            for mood in moods:
                line += ' █' if mood >= level else '  '
            graph_lines.append(line)
        graph_lines.append('   +' + '-' * (len(moods) * 2))
        days = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'][-len(moods):]
        graph_lines.append('    ' + ' '.join(days))
        return '\n'.join(graph_lines)
    
    def _build_stress_trend(self, anxieties):
        if not anxieties:
            return ''
        avg_stress = sum(anxieties) / len(anxieties)
        trend = ''
        for stress in anxieties:
            if stress < avg_stress - 1:
                trend += '↓ '
            elif stress > avg_stress + 1:
                trend += '↑ '
            else:
                trend += '→ '
        avg_level = '🟢 Low' if avg_stress < 4 else ('🟡 Medium' if avg_stress < 7 else '🔴 High')
        return f'Trend: {trend}\nOverall: {avg_level} (avg {avg_stress:.1f})'

class SelfCareScreen(Screen):
    def on_enter(self):
        self.load_selfcare_menu()

    def load_selfcare_menu(self):
        self.ids.selfcare_grid.clear_widgets()
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        self.ids.selfcare_grid.add_widget(Label(text='Self-Care Tools', size_hint_y=None, height=50))
        self.ids.selfcare_grid.add_widget(Label(text='Choose a self-care activity:', size_hint_y=None, height=40))
        
        # Buttons for different self-care options
        btn_breathing = Button(text='🌬️ Breathing Exercises', size_hint_y=None, height=50)
        btn_breathing.bind(on_press=self.show_breathing_exercises)
        self.ids.selfcare_grid.add_widget(btn_breathing)
        
        btn_journaling = Button(text='📝 Journaling', size_hint_y=None, height=50)
        btn_journaling.bind(on_press=self.show_journaling)
        self.ids.selfcare_grid.add_widget(btn_journaling)
        
        btn_music = Button(text='🎵 Relaxing Music', size_hint_y=None, height=50)
        btn_music.bind(on_press=self.show_music)
        self.ids.selfcare_grid.add_widget(btn_music)
        
        btn_tips = Button(text='✨ Positive Tips', size_hint_y=None, height=50)
        btn_tips.bind(on_press=self.show_positive_tips)
        self.ids.selfcare_grid.add_widget(btn_tips)
    
    def show_breathing_exercises(self, instance):
        self.ids.selfcare_grid.clear_widgets()
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        self.ids.selfcare_grid.add_widget(Label(text='Breathing Exercises', font_size=20, size_hint_y=None, height=50))
        breathing_guide = (
            "4-7-8 Breathing Technique:\n\n"
            "1. Exhale completely through your mouth\n"
            "2. Close your mouth, inhale through nose for 4 counts\n"
            "3. Hold your breath for 7 counts\n"
            "4. Exhale through mouth for 8 counts\n"
            "5. Repeat 4 times\n\n"
            "Benefits: Reduces anxiety, improves focus, promotes relaxation"
        )
        self.ids.selfcare_grid.add_widget(Label(text=breathing_guide, text_size=(self.width - 40, None), size_hint_y=None, height=250))
        
        btn_back = Button(text='Back to Self-Care Menu', size_hint_y=None, height=50)
        btn_back.bind(on_press=lambda x: self.load_selfcare_menu())
        self.ids.selfcare_grid.add_widget(btn_back)
    
    def show_journaling(self, instance):
        self.ids.selfcare_grid.clear_widgets()
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.textinput import TextInput
        
        self.ids.selfcare_grid.add_widget(Label(text='Journaling', font_size=20, size_hint_y=None, height=40))
        self.ids.selfcare_grid.add_widget(Label(text='Write your thoughts and feelings:', size_hint_y=None, height=30))
        
        journal_input = TextInput(text='', multiline=True, size_hint_y=0.6)
        self.ids.selfcare_grid.add_widget(journal_input)
        
        def save_journal(btn):
            if journal_input.text.strip():
                app = App.get_running_app()
                app.db.add_checkin(datetime.now().strftime('%Y-%m-%d'), 5, 5, 8, 'Journaling', journal_input.text)
                from kivy.uix.label import Label as MsgLabel
                self.ids.selfcare_grid.add_widget(MsgLabel(text='Journal saved!', size_hint_y=None, height=40))
        
        btn_save = Button(text='Save Journal Entry', size_hint_y=None, height=50)
        btn_save.bind(on_press=save_journal)
        self.ids.selfcare_grid.add_widget(btn_save)
        
        btn_back = Button(text='Back to Self-Care Menu', size_hint_y=None, height=50)
        btn_back.bind(on_press=lambda x: self.load_selfcare_menu())
        self.ids.selfcare_grid.add_widget(btn_back)
    
    def show_music(self, instance):
        self.ids.selfcare_grid.clear_widgets()
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        self.ids.selfcare_grid.add_widget(Label(text='Relaxing Music', font_size=20, size_hint_y=None, height=50))
        music_info = (
            "Recommended Relaxing Music Platforms:\n\n"
            "🎵 Spotify: Search for 'Calm', 'Meditation', 'Sleep Sounds'\n"
            "🎵 YouTube: 'Deep Sleep Music', 'Peaceful Piano', 'Nature Sounds'\n"
            "🎵 Apple Music: Curated playlists for 'Focus', 'Relaxation'\n\n"
            "Benefits:\n"
            "• Reduces stress and anxiety\n"
            "• Improves sleep quality\n"
            "• Enhances focus and concentration\n\n"
            "Tip: Listen for 15-30 minutes daily for best results."
        )
        self.ids.selfcare_grid.add_widget(Label(text=music_info, text_size=(self.width - 40, None), size_hint_y=None, height=320))
        
        btn_back = Button(text='Back to Self-Care Menu', size_hint_y=None, height=50)
        btn_back.bind(on_press=lambda x: self.load_selfcare_menu())
        self.ids.selfcare_grid.add_widget(btn_back)
    
    def show_positive_tips(self, instance):
        self.ids.selfcare_grid.clear_widgets()
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        self.ids.selfcare_grid.add_widget(Label(text='Positive Tips', font_size=20, size_hint_y=None, height=50))
        
        tips = [
            "✨ You are stronger than you think.",
            "💪 Every small step forward counts.",
            "🌟 Your feelings are valid.",
            "💖 Be kind to yourself, always.",
            "🌈 This too shall pass.",
            "🧘 Focus on what you can control.",
            "🌸 Growth happens outside your comfort zone.",
            "💫 You deserve happiness and peace.",
            "🔥 Challenges make you stronger.",
            "🌻 One day at a time is enough."
        ]
        
        for tip in tips:
            self.ids.selfcare_grid.add_widget(Label(text=tip, text_size=(self.width - 40, None), size_hint_y=None, height=50))
        
        btn_back = Button(text='Back to Self-Care Menu', size_hint_y=None, height=50)
        btn_back.bind(on_press=lambda x: self.load_selfcare_menu())
        self.ids.selfcare_grid.add_widget(btn_back)

class EmergencyScreen(Screen):
    def on_enter(self):
        if hasattr(self.ids, 'call_status'):
            self.ids.call_status.text = ''

    def call_helpline(self, number):
        if hasattr(self.ids, 'call_status'):
            self.ids.call_status.text = f'Calling {number}... If you are on a device, use your phone to dial this number now.'

class WellNestApp(App):
    current_user = StringProperty('')

    def build(self):
        self.db = Database()
        sm = ScreenManager()
        sm.add_widget(SplashScreen(name='splash'))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(ProfileScreen(name='profile'))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(CheckInScreen(name='checkin'))
        sm.add_widget(HistoryScreen(name='history'))
        sm.add_widget(SupportCircleScreen(name='support'))
        sm.add_widget(WeeklyReportScreen(name='weekly'))
        sm.add_widget(SelfCareScreen(name='selfcare'))
        sm.add_widget(EmergencyScreen(name='emergency'))
        sm.current = 'splash'
        return sm

if __name__ == '__main__':
    app = WellNestApp()
    app.run()