import flet as ft
import requests
import json

def main(page: ft.Page):
    page.title = "Fierritos RAG"
    page.window_width = 1000
    page.window_height = 800
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#121212"
    page.padding = 20
    
    # Color scheme based on logo
    primary_color = "#D38B5D"  # Copper/bronze color
    secondary_color = "#121212"  # Dark background
    accent_color = "#F0A06A"  # Lighter copper
    danger_color = "#B44C1B"  # Darker copper for danger
    text_color = "#FFFFFF"  # White text
    
    API_URL = "http://localhost:8000/api/v1"
    token = None
    documents_list = []

    def show_snackbar(message, color="green"):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.colors.WHITE),
            bgcolor=color
        )
        page.snack_bar.open = True
        page.update()

    def close_dialog(e, dialog):
        dialog.open = False
        page.update()

    # Function to toggle summary visibility
    def toggle_summary(e, doc_id):
        # Find the document control in the list
        for control in documents_list_view.controls:
            if hasattr(control, 'data') and control.data == doc_id:
                # Toggle the visibility of the summary container
                summary_container = control.content.content.controls[1]
                summary_container.visible = not summary_container.visible
                
                # Update button text based on visibility
                toggle_button = control.content.content.controls[0].controls[2]
                toggle_button.text = "Hide Summary" if summary_container.visible else "Show Summary"
                page.update()
                break

    # Logo component to be shown in app bar
    def create_logo():
        return ft.Container(
            content=ft.Column([
                ft.Text("FIERRITOS SAS", 
                      color=primary_color, 
                      weight=ft.FontWeight.BOLD,
                      size=14),
                ft.Text("IA TECHNOLOGY", 
                      color=primary_color, 
                      size=10)
            ], spacing=0, alignment=ft.MainAxisAlignment.CENTER),
            border=ft.border.all(color=primary_color, width=2),
            border_radius=30,
            padding=ft.padding.all(10),
            width=120,
            height=50,
        )
    
    # Navigation drawer and App Bar
    def build_app_bar(title):
        return ft.AppBar(
            leading=create_logo(),
            leading_width=140,
            title=ft.Text(title, weight=ft.FontWeight.BOLD, color=text_color),
            center_title=False,
            bgcolor=secondary_color,
            toolbar_height=70,
            actions=[
                ft.IconButton(
                    icon=ft.icons.LOGOUT,
                    icon_color=primary_color,
                    tooltip="Logout",
                    on_click=logout,
                ),
            ] if token else [],
        )

    # Logout function
    async def logout(e):
        nonlocal token
        token = None
        show_snackbar("Logged out successfully")
        page.go("/login")
        page.update()

    # Input fields
    email_input = ft.TextField(
        label="Email",
        border=ft.InputBorder.OUTLINE,
        width=350,
        prefix_icon=ft.icons.EMAIL
    )
    
    password_input = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        border=ft.InputBorder.OUTLINE,
        width=350,
        prefix_icon=ft.icons.LOCK
    )
    
    confirm_password_input = ft.TextField(
        label="Confirm Password",
        password=True,
        can_reveal_password=True,
        border=ft.InputBorder.OUTLINE,
        width=350,
        prefix_icon=ft.icons.LOCK_RESET
    )
    
    name_input = ft.TextField(
        label="Full Name",
        border=ft.InputBorder.OUTLINE,
        width=350,
        prefix_icon=ft.icons.PERSON
    )

    # Documents components
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    
    documents_dropdown = ft.Dropdown(
        width=350,
        label="Select Document",
        border=ft.InputBorder.OUTLINE,
        prefix_icon=ft.icons.DESCRIPTION
    )
    
    question_input = ft.TextField(
        label="Question",
        width=350,
        multiline=True,
        min_lines=2,
        max_lines=4,
        border=ft.InputBorder.OUTLINE,
        prefix_icon=ft.icons.QUESTION_ANSWER
    )
    
    documents_list_view = ft.ListView(
        spacing=10,
        padding=20,
        auto_scroll=True,
        expand=True
    )
    
    answer_container = ft.Container(
        content=ft.Column([
            ft.Text("Answer", weight=ft.FontWeight.BOLD, size=22, color=secondary_color),
            ft.Container(
                content=ft.Text("", size=16),
                bgcolor=accent_color,
                border_radius=10,
                padding=15,
                width=700,
                height=250,
                border=ft.border.all(1, ft.colors.BLUE_200),
            )
        ]),
        visible=False
    )

    async def register(e):
        try:
            # Validar contraseña
            if (password_input.value != confirm_password_input.value):
                show_snackbar("Passwords don't match", "red")
                return
                
            if len(password_input.value) < 8:
                show_snackbar("Password must be at least 8 characters", "red")
                return

            # Validar email
            if not email_input.value or '@' not in email_input.value:
                show_snackbar("Invalid email format", "red")
                return

            response = requests.post(
                f"{API_URL}/auth/register",
                json={
                    'email': email_input.value,
                    'password': password_input.value
                }
            )
            
            if response.status_code == 400:
                show_snackbar("Email already registered", "red")
                return
            elif response.status_code == 422:
                show_snackbar("Invalid data. Check email and password", "red")
                return
                
            response.raise_for_status()
            show_snackbar("Registration successful! Please login.")
            # Limpiar campos
            email_input.value = ""
            password_input.value = ""
            confirm_password_input.value = ""
            page.go("/login")
            
        except Exception as e:
            show_snackbar(f"Registration error: {str(e)}", "red")
        page.update()

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
        nonlocal documents_list
        try:
            response = requests.get(
                f"{API_URL}/documents/documents",
                headers={'Authorization': f'Bearer {token}'}
            )
            response.raise_for_status()
            documents_list = response.json()
            
            # Update dropdown
            documents_dropdown.options = [
                ft.dropdown.Option(
                    key=str(doc['id']),
                    text=doc['title']
                ) for doc in documents_list
            ]
            
            # Update documents list view
            documents_list_view.controls.clear()
            for doc in documents_list:
                doc_id = doc['id']
                doc_title = doc['title']
                summary_text = doc.get('summary', 'No summary available') or "No summary available"
                
                # Create a card for each document
                doc_card = ft.Card(
                    data=doc_id,  # Store document ID for reference
                    content=ft.Container(
                        content=ft.Column([
                            # Top row with document info and buttons
                            ft.Row(
                                [
                                    ft.Icon(ft.icons.DESCRIPTION, color=primary_color, size=30),
                                    ft.Column(
                                        [
                                            ft.Text(doc_title, weight=ft.FontWeight.BOLD),
                                            ft.Text(f"Created: {doc['created_at'][:10]}", size=12, color=ft.colors.GREY_700),
                                        ],
                                        spacing=5,
                                        expand=True
                                    ),
                                    ft.ElevatedButton(
                                        "Show Summary",
                                        icon=ft.icons.SUMMARIZE,
                                        style=ft.ButtonStyle(
                                            color=ft.colors.WHITE,
                                            bgcolor=accent_color,
                                        ),
                                        on_click=lambda e, doc_id=doc_id: toggle_summary(e, doc_id)
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE,
                                        icon_color=danger_color,
                                        tooltip="Delete document",
                                        data=doc_id,
                                        on_click=confirm_delete_document
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            # Summary container (initially hidden)
                            ft.Container(
                                content=ft.Column([
                                    ft.Divider(),
                                    ft.Text("Summary:", weight=ft.FontWeight.BOLD),
                                    ft.Container(
                                        content=ft.Text(summary_text, color=secondary_color),
                                        bgcolor=accent_color,
                                        border_radius=5,
                                        padding=10,
                                        expand=True
                                    )
                                ]),
                                visible=False  # Initially hidden
                            )
                        ]),
                        padding=15
                    ),
                    elevation=2
                )
                
                documents_list_view.controls.append(doc_card)
            page.update()
        except Exception as e:
            show_snackbar(f"Failed to load documents: {str(e)}", "red")

    def confirm_delete_document(e):
        # Create a dialog for confirmation
        document_id = e.control.data
        document_title = next((doc['title'] for doc in documents_list if doc['id'] == document_id), "this document")
        
        dialog = ft.AlertDialog(
            title=ft.Text("Confirm Deletion"),
            content=ft.Text(f"Are you sure you want to delete '{document_title}'? This cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: close_dialog(e, dialog)),
                ft.TextButton(
                    "Delete", 
                    on_click=lambda e: delete_document(e, document_id, dialog),
                    style=ft.ButtonStyle(color=danger_color)
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    async def delete_document(e, document_id, dialog):
        try:
            response = requests.delete(
                f"{API_URL}/documents/documents/{document_id}",
                headers={'Authorization': f'Bearer {token}'}
            )
            response.raise_for_status()
            
            # Close dialog
            dialog.open = False
            
            # Reload documents
            await load_documents()
            show_snackbar("Document deleted successfully")
        except Exception as e:
            show_snackbar(f"Failed to delete document: {str(e)}", "red")
        page.update()

    async def upload_file(e: ft.FilePickerResultEvent):
        if not e.files or not e.files[0]:
            show_snackbar("No file selected", "red")
            return

        file = e.files[0]
        try:
            # Create form-data with the file
            files = {'file': (file.name, open(file.path, 'rb'), 'application/octet-stream')}
            
            # Show progress
            progress_ring.visible = True
            page.update()
            
            response = requests.post(
                f"{API_URL}/documents/upload",
                headers={'Authorization': f'Bearer {token}'},
                files=files
            )
            response.raise_for_status()
            
            # Hide progress
            progress_ring.visible = False
            
            # Update documents list
            await load_documents()
            show_snackbar("File uploaded successfully!")
            
        except Exception as e:
            progress_ring.visible = False
            show_snackbar(f"Failed to upload file: {str(e)}", "red")
        page.update()

    async def ask_question(e):
        if not documents_dropdown.value or not question_input.value:
            show_snackbar("Please select a document and enter a question", "red")
            return
        try:
            # Show loading state
            progress_ring.visible = True
            answer_container.visible = True
            answer_container.content.controls[1].content.value = "Processing question..."
            page.update()
            
            # Build URL with query parameters
            document_id = documents_dropdown.value
            question = question_input.value
            
            response = requests.post(
                f"{API_URL}/documents/ask/{document_id}",
                params={'question': question},
                headers={'Authorization': f'Bearer {token}'}
            )
            
            # Hide progress
            progress_ring.visible = True
            
            if response.status_code == 404:
                show_snackbar("Document not found", "red")
                answer_container.content.controls[1].content.value = ""
            else:
                response.raise_for_status()
                answer = response.json().get('answer', 'Could not get an answer')
                answer_container.content.controls[1].content.value = answer
                show_snackbar("Question answered successfully!")
                
        except Exception as e:
            progress_ring.visible = False
            show_snackbar(f"Error getting response: {str(e)}", "red")
            answer_container.content.controls[1].content.value = ""
        finally:
            page.update()

    file_picker.on_result = upload_file
    
    # Progress indicator
    progress_ring = ft.ProgressRing(
        width=20,
        height=20,
        stroke_width=2,
        visible=False
    )

    # Views
    register_view = ft.View(
        "/register",
        [
            build_app_bar("Register New Account"),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=create_logo(),
                            alignment=ft.alignment.center,
                            padding=20,
                            width=200,
                            height=200,
                        ),
                        ft.Text("Create a new account", size=24, text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD),
                        name_input,
                        email_input,
                        password_input,
                        confirm_password_input,
                        ft.Container(height=20),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "Register",
                                    on_click=register,
                                    style=ft.ButtonStyle(
                                        color=text_color,
                                        bgcolor=primary_color,
                                        padding=15,
                                    ),
                                    width=350
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Text("Already have an account?"),
                                    ft.TextButton("Login", on_click=lambda _: page.go("/login"))
                                ],
                                alignment=ft.MainAxisAlignment.CENTER
                            )
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15
                ),
                padding=20,
                alignment=ft.alignment.center,
            ),
        ],
        padding=0
    )

    login_view = ft.View(
        "/login",
        [
            build_app_bar("Login"),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=create_logo(),
                            alignment=ft.alignment.center,
                            padding=20,
                            width=200,
                            height=200,
                        ),
                        ft.Text("Welcome Back", size=28, text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD),
                        ft.Text("Login to your account", size=16, color=ft.colors.GREY_700),
                        ft.Container(height=20),
                        email_input,
                        password_input,
                        ft.Container(height=20),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "Login",
                                    on_click=login,
                                    style=ft.ButtonStyle(
                                        color=text_color,
                                        bgcolor=primary_color,
                                        padding=15,
                                    ),
                                    width=350
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Text("Don't have an account?"),
                                    ft.TextButton("Register", on_click=lambda _: page.go("/register"))
                                ],
                                alignment=ft.MainAxisAlignment.CENTER
                            )
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15
                ),
                padding=20,
                alignment=ft.alignment.center,
            ),
        ],
        padding=0
    )

    documents_view = ft.View(
        "/documents",
        [
            build_app_bar("Document Management"),
            ft.Tabs(
                selected_index=0,
                animation_duration=300,
                tabs=[
                    ft.Tab(
                        text="Documents",
                        icon=ft.icons.FOLDER,
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Text("My Documents", size=20, weight=ft.FontWeight.BOLD),
                                            ft.Row(
                                                [
                                                    ft.ElevatedButton(
                                                        "Upload New Document",
                                                        icon=ft.icons.UPLOAD_FILE,
                                                        on_click=lambda _: file_picker.pick_files(),
                                                        style=ft.ButtonStyle(
                                                            color=text_color,
                                                            bgcolor=primary_color,
                                                        ),
                                                    ),
                                                    progress_ring,
                                                ],
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    ),
                                    ft.Divider(),
                                    documents_list_view,
                                ],
                            ),
                            padding=20,
                        ),
                    ),
                    ft.Tab(
                        text="Ask Questions",
                        icon=ft.icons.QUESTION_ANSWER,
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Ask a Question", size=20, weight=ft.FontWeight.BOLD),
                                    ft.Card(
                                        content=ft.Container(
                                            content=ft.Column(
                                                [
                                                    documents_dropdown,
                                                    question_input,
                                                    ft.Container(
                                                        content=ft.ElevatedButton(
                                                            "Ask Question",
                                                            icon=ft.icons.SEND,
                                                            on_click=ask_question,
                                                            style=ft.ButtonStyle(
                                                                color=ft.colors.WHITE,
                                                                bgcolor=primary_color,
                                                            ),
                                                        ),
                                                        alignment=ft.alignment.center_right,
                                                        margin=ft.margin.only(top=10)
                                                    ),
                                                ],
                                                spacing=15,
                                            ),
                                            padding=20,
                                        ),
                                        elevation=3,
                                        margin=10,
                                    ),
                                    answer_container,
                                ],
                                spacing=20,
                            ),
                            padding=20,
                        ),
                    ),
                ],
                expand=1,
            ),
        ],
        padding=0
    )

    def route_change(e):
        if page.route == "/documents":
            page.views.clear()
            page.views.append(documents_view)
        elif page.route == "/register":
            page.views.clear()
            page.views.append(register_view)
        else:  # "/login" o ruta por defecto
            page.views.clear()
            page.views.append(login_view)
        page.update()

    page.on_route_change = route_change
    page.go("/login")  # Cambiar la ruta inicial a login

ft.app(target=main, port=8001)