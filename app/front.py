import flet as ft
import requests
import json

def main(page: ft.Page):
   page.title = "RAG SaaS"
   page.window_width = 800
   page.window_height = 800

   API_URL = "http://localhost:8000/api/v1"
   token = None

   def show_snackbar(message, color="green"):
       page.snack_bar = ft.SnackBar(
           content=ft.Text(message),
           bgcolor=color
       )
       page.snack_bar.open = True
       page.update()

   email_input = ft.TextField(label="Email", width=300)
   password_input = ft.TextField(label="Password", password=True, width=300)
   file_picker = ft.FilePicker()
   page.overlay.append(file_picker)
   documents_dropdown = ft.Dropdown(width=300, label="Select Document")
   question_input = ft.TextField(label="Question", width=300, multiline=True)
   answer_text = ft.Text(size=16, width=300)

   async def login(e):
       nonlocal token
       try:
           response = requests.post(
               f"{API_URL}/auth/token",
               data={
                   'username': email_input.value,
                   'password': password_input.value
               }
           )
           response.raise_for_status()
           token = response.json()['access_token']
           show_snackbar("Login successful!")
           await load_documents()
           page.go("/documents")
       except Exception as e:
           show_snackbar(f"Login failed: {str(e)}", "red")
       page.update()

   async def load_documents():
       try:
           response = requests.get(
               f"{API_URL}/documents/documents",
               headers={'Authorization': f'Bearer {token}'}
           )
           response.raise_for_status()
           docs = response.json()
           documents_dropdown.options = [
               ft.dropdown.Option(key=str(doc['id']), text=doc['title'])
               for doc in docs
           ]
           page.update()
       except Exception as e:
           show_snackbar(f"Failed to load documents: {str(e)}", "red")

   async def upload_file(e):
       if not e.files:
           return
       try:
           files = {'file': (
               e.files[0].name,
               open(e.files[0].path, 'rb'),
               'application/octet-stream'
           )}
           response = requests.post(
               f"{API_URL}/documents/upload",
               headers={'Authorization': f'Bearer {token}'},
               files=files
           )
           response.raise_for_status()
           show_snackbar(f"File uploaded successfully!")
           await load_documents()
       except Exception as e:
           show_snackbar(f"Upload failed: {str(e)}", "red")
       page.update()

   async def ask_question(e):
       if not documents_dropdown.value or not question_input.value:
           show_snackbar("Please select a document and enter a question", "red")
           return
       try:
           response = requests.post(
               f"{API_URL}/documents/ask/{documents_dropdown.value}",
               headers={
                   'Authorization': f'Bearer {token}',
                   'Content-Type': 'application/json'
               },
               json={'question': question_input.value}
           )
           response.raise_for_status()
           answer = response.json()['answer']
           answer_text.value = answer
           show_snackbar("Question answered successfully!")
       except Exception as e:
           show_snackbar(f"Failed to get answer: {str(e)}", "red")
       page.update()

   file_picker.on_result = upload_file

   login_view = ft.Column(
       controls=[
           ft.Text("Login", size=32, weight=ft.FontWeight.BOLD),
           email_input,
           password_input,
           ft.ElevatedButton("Login", on_click=login)
       ],
       alignment=ft.MainAxisAlignment.CENTER,
       spacing=20
   )

   documents_view = ft.Column(
       controls=[
           ft.Text("Document Management", size=32, weight=ft.FontWeight.BOLD),
           ft.ElevatedButton(
               "Upload Document",
               icon=ft.icons.UPLOAD_FILE,
               on_click=lambda _: file_picker.pick_files()
           ),
           ft.Divider(),
           ft.Text("Ask Questions", size=20),
           documents_dropdown,
           question_input,
           ft.ElevatedButton("Ask", on_click=ask_question),
           answer_text
       ],
       alignment=ft.MainAxisAlignment.START,
       spacing=20
   )

   def route_change(e):
       page.views.clear()
       if page.route == "/documents":
           page.views.append(
               ft.View("/documents", [documents_view])
           )
       else:
           page.views.append(
               ft.View("/", [login_view])
           )
       page.update()

   page.on_route_change = route_change
   page.go(page.route)

ft.app(target=main, port=8001)