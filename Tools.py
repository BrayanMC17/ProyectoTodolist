import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

# =========================
# Configuración de la base de datos
# =========================
Base = declarative_base()
engine = create_engine('sqlite:///tool_list.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# =========================
# Modelo de datos
# =========================
class Tool(Base):
    __tablename__ = 'tools'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    text = Column(String(200), nullable=False)
    status = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Tool(title='{self.title}', status={'Activo' if self.status else 'Inactivo'})>"

# Crear las tablas si no existen
Base.metadata.create_all(engine)

# =========================
# Funciones CRUD
# =========================
def add_tool(title, text, status):
    session.add(Tool(title=title, text=text, status=status))
    session.commit()

def get_all_tools():
    return session.query(Tool).all()

def get_tool_by_id(tool_id):
    return session.query(Tool).filter(Tool.id == tool_id).first()

def update_tool(tool_id, new_title=None, new_text=None, new_status=None):
    tool = get_tool_by_id(tool_id)
    if tool:
        if new_title: tool.title = new_title
        if new_text: tool.text = new_text
        if new_status is not None: tool.status = new_status
        session.commit()

def delete_tool(tool_id):
    tool = get_tool_by_id(tool_id)
    if tool:
        session.delete(tool)
        session.commit()

# =========================
# Funciones Importar/Exportar JSON
# =========================
def export_tools_to_json():
    tools = get_all_tools()
    data = [{"id": tool.id, "title": tool.title, "text": tool.text, "status": tool.status} for tool in tools]
    json_data = json.dumps(data, indent=4)

    st.download_button(
        label="⬇️ Descargar herramientas como JSON",
        data=json_data,
        file_name="tools.json",
        mime="application/json"
    )

def import_tools_from_json():
    uploaded_file = st.file_uploader("Carga un archivo JSON con herramientas", type=["json"])
    if uploaded_file:
        try:
            data = json.load(uploaded_file)
            if not isinstance(data, list):
                st.error("❌ El archivo JSON debe contener una lista de herramientas.")
                return

            for tool_data in data:
                if "title" in tool_data and "text" in tool_data and "status" in tool_data:
                    session.add(Tool(
                        title=tool_data["title"],
                        text=tool_data["text"],
                        status=tool_data["status"]
                    ))
                else:
                    st.warning(f"❗ Herramienta incompleta encontrada: {tool_data}. Fue ignorada.")

            session.commit()
            st.success("✔️ Herramientas importadas correctamente.")
        except Exception as e:
            st.error(f"❌ Error al procesar el archivo: {e}")

# =========================
# Interfaz de Streamlit
# =========================
def app():
    st.title("Tool List App 🛠️")
    st.sidebar.title("Menú Principal")
    menu = ["Agregar Herramienta", "Ver Herramientas", "Actualizar Herramienta", "Eliminar Herramienta", "Exportar a JSON", "Importar desde JSON"]
    opcion = st.sidebar.radio("Selecciona una opción", menu)

    if opcion == "Agregar Herramienta":
        st.header("Agregar una nueva herramienta")
        title = st.text_input("Título")
        text = st.text_area("Texto")
        status = st.checkbox("¿Está activa?")
        if st.button("Guardar"):
            if title and text:
                add_tool(title, text, status)
                st.success("✔️ Herramienta agregada correctamente.")
            else:
                st.error("❌ Por favor completa todos los campos.")

    elif opcion == "Ver Herramientas":
        st.header("Lista de herramientas")
        tools = get_all_tools()
        if tools:
            for tool in tools:
                st.write(f"**{tool.title}**")
                st.write(f"Descripción: {tool.text}")
                st.write(f"Estado: {'Activo ✅' if tool.status else 'Inactivo ❌'}")
                st.write("---")
        else:
            st.info("📋 No hay herramientas registradas.")

    elif opcion == "Actualizar Herramienta":
        st.header("Actualizar una herramienta")
        tools = get_all_tools()
        if tools:
            tool_choices = {tool.id: tool.title for tool in tools}
            tool_id = st.selectbox("Selecciona una herramienta", tool_choices.keys(), format_func=lambda x: tool_choices[x])
            tool = get_tool_by_id(tool_id)

            new_title = st.text_input("Nuevo título", value=tool.title)
            new_text = st.text_area("Nuevo texto", value=tool.text)
            new_status = st.checkbox("¿Está activa?", value=tool.status)
            if st.button("Guardar cambios"):
                update_tool(tool_id, new_title, new_text, new_status)
                st.success("✔️ Herramienta actualizada correctamente.")
        else:
            st.warning("📋 No hay herramientas registradas.")

    elif opcion == "Eliminar Herramienta":
        st.header("Eliminar una herramienta")
        tools = get_all_tools()
        if tools:
            tool_choices = {tool.id: tool.title for tool in tools}
            tool_id = st.selectbox("Selecciona una herramienta", tool_choices.keys(), format_func=lambda x: tool_choices[x])
            if st.button("Eliminar"):
                delete_tool(tool_id)
                st.success("✔️ Herramienta eliminada correctamente.")
        else:
            st.warning("📋 No hay herramientas registradas.")

    elif opcion == "Exportar a JSON":
        st.header("Exportar herramientas a JSON")
        export_tools_to_json()

    elif opcion == "Importar desde JSON":
        st.header("Importar herramientas desde JSON")
        import_tools_from_json()

# =========================
# Ejecutar la aplicación
# =========================
if __name__ == "__main__":
    app()
