import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

# Configuración de la base de datos
Base = declarative_base()
engine = create_engine('sqlite:///tool_list.db', echo=True)  # Base de datos SQLite
Session = sessionmaker(bind=engine)
session = Session()

# Modelo de datos
class Tool(Base):
    __tablename__ = 'tools'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    text = Column(String(200), nullable=False)
    status = Column(Boolean, default=False)  # False = Inactivo, True = Activo

    def __repr__(self):
        return f"<Tool(title='{self.title}', status={'Activo' if self.status else 'Inactivo'})>"

# Crear las tablas en la base de datos (si no existen)
Base.metadata.create_all(engine)

# Funciones CRUD
def add_tool(title, text, status):
    tool = Tool(title=title, text=text, status=status)
    session.add(tool)
    session.commit()

def get_all_tools():
    return session.query(Tool).all()

def update_tool(tool_id, new_title=None, new_text=None, new_status=None):
    tool = session.query(Tool).filter(Tool.id == tool_id).first()
    if tool:
        if new_title is not None:
            tool.title = new_title
        if new_text is not None:
            tool.text = new_text
        if new_status is not None:
            tool.status = new_status
        session.commit()

def delete_tool(tool_id):
    tool = session.query(Tool).filter(Tool.id == tool_id).first()
    if tool:
        session.delete(tool)
        session.commit()

# Funciones de Exportar e Importar JSON
def export_tools_to_json():
    # Obtener todas las herramientas
    tools = get_all_tools()
    
    # Convertir las herramientas a un formato JSON
    data = [
        {"id": tool.id, "title": tool.title, "text": tool.text, "status": tool.status}
        for tool in tools
    ]
    
    # Convertir el contenido a un string JSON
    json_data = json.dumps(data, indent=4)  # Agregamos indentación para mejor legibilidad
    
    # Crear un botón de descarga en Streamlit
    st.download_button(
        label="⬇️ Descargar herramientas como JSON",
        data=json_data,  # El contenido a descargar
        file_name="tools.json",  # Nombre del archivo descargable
        mime="application/json"  # Tipo de contenido
    )

def import_tools_from_json():
    # Permitir que el usuario cargue un archivo JSON
    uploaded_file = st.file_uploader("Carga un archivo JSON con herramientas", type=["json"])

    if uploaded_file is not None:
        try:
            # Leer el contenido del archivo cargado como un string JSON
            data = json.load(uploaded_file)

            # Validar que el archivo JSON contenga una lista de herramientas
            if not isinstance(data, list):
                st.error("❌ El archivo JSON debe contener una lista de herramientas.")
                return

            # Procesar cada herramienta en el archivo JSON
            for tool_data in data:
                # Validar que los campos requeridos estén presentes en cada entrada
                if "title" in tool_data and "text" in tool_data and "status" in tool_data:
                    # Crear una nueva herramienta y agregarla a la base de datos
                    new_tool = Tool(
                        title=tool_data["title"],
                        text=tool_data["text"],
                        status=tool_data["status"]
                    )
                    session.add(new_tool)
                else:
                    st.warning(f"❗ Herramienta incompleta encontrada: {tool_data}. Fue ignorada.")
            
            # Guardar todos los cambios en la base de datos
            session.commit()
            st.success("✔️ Herramientas importadas correctamente desde el archivo JSON.")
        except json.JSONDecodeError:
            st.error("❌ Error al leer el archivo JSON. Asegúrate de que esté correctamente formateado.")
        except Exception as e:
            st.error(f"❌ Ocurrió un error inesperado: {str(e)}")
    else:
        st.info("📂 Carga un archivo JSON para importar herramientas.")

# Interfaz con Streamlit
def app():
    st.title("Tool List App con Importar/Exportar JSON")

    menu = ["Agregar Herramienta", "Ver Herramientas", "Actualizar Herramienta", "Eliminar Herramienta", "Exportar a JSON", "Importar desde JSON"]
    opcion = st.sidebar.selectbox("Menú", menu)

    if opcion == "Agregar Herramienta":
        st.subheader("Agregar una nueva herramienta")
        title = st.text_input("Título")
        text = st.text_area("Texto")
        status = st.checkbox("¿Está activa?")
        if st.button("Guardar Herramienta"):
            if title and text:
                add_tool(title, text, status)
                st.success("Herramienta agregada correctamente.")
            else:
                st.error("Por favor llena todos los campos.")

    elif opcion == "Ver Herramientas":
        st.subheader("Lista de herramientas")
        tools = get_all_tools()
        if tools:
            for tool in tools:
                st.write(f"ID: {tool.id}, Título: {tool.title}, Estado: {'Activo' if tool.status else 'Inactivo'}")
                st.write(f"Descripción: {tool.text}")
                st.write("---")
        else:
            st.warning("No hay herramientas registradas.")

    elif opcion == "Actualizar Herramienta":
        st.subheader("Actualizar una herramienta")
        tools = get_all_tools()
        if tools:
            tool_choices = {tool.id: tool.title for tool in tools}
            tool_id = st.selectbox("Selecciona la herramienta a actualizar", list(tool_choices.keys()), format_func=lambda x: tool_choices[x])
            new_title = st.text_input("Nuevo título", value=session.query(Tool).filter(Tool.id == tool_id).first().title)
            new_text = st.text_area("Nuevo texto", value=session.query(Tool).filter(Tool.id == tool_id).first().text)
            new_status = st.checkbox("¿Está activa?", value=session.query(Tool).filter(Tool.id == tool_id).first().status)
            if st.button("Guardar Cambios"):
                update_tool(tool_id, new_title, new_text, new_status)
                st.success("Herramienta actualizada correctamente.")
        else:
            st.warning("No hay herramientas registradas.")

    elif opcion == "Eliminar Herramienta":
        st.subheader("Eliminar una herramienta")
        tools = get_all_tools()
        if tools:
            tool_choices = {tool.id: tool.title for tool in tools}
            tool_id = st.selectbox("Selecciona la herramienta a eliminar", list(tool_choices.keys()), format_func=lambda x: tool_choices[x])
            if st.button("Eliminar Herramienta"):
                delete_tool(tool_id)
                st.success("Herramienta eliminada correctamente.")
        else:
            st.warning("No hay herramientas registradas.")

    elif opcion == "Exportar a JSON":
        st.subheader("Exportar Herramientas")
        if st.button("Exportar"):
            export_tools_to_json()

    elif opcion == "Importar desde JSON":
        st.subheader("Importar Herramientas")
        import_tools_from_json()

# Ejecutar la aplicación
if __name__ == "__main__":
    app()
