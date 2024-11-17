import streamlit as st
import pandas as pd
import google.generativeai as genai

# Initialize Gemini API
def initialize_gemini():
    genai.configure(api_key="AIzaSyCCQumrGPGSzDgY7_YFSSI5kFzYb-WXFB4")  # ใส่ API key ของคุณที่นี่
    return genai.GenerativeModel('gemini-pro')

# Load CSV data
def load_hr_data():
    try:
        employee_data = pd.read_csv('employee_data_1511.csv')
        employee_skills = pd.read_csv('employee_skills_1511.csv')
        feedback_data = pd.read_csv('feedback_data_th.csv')
        kpi_data = pd.read_csv('kpi_data.csv')
        leave_data = pd.read_csv('leave_data_up.csv')
        task_data = pd.read_csv('task_data2_edit.csv')
        
        return {
            'employee_data': employee_data,
            'employee_skills': employee_skills,
            'feedback_data': feedback_data,
            'kpi_data': kpi_data,
            'leave_data': leave_data,
            'task_data': task_data
        }
    except Exception as e:
        st.error(f"Error loading CSV files: {str(e)}")
        return None

def get_gemini_response(model, question, data_context):
    try:
        prompt = f"""คุณเป็น HR Analyst ที่เชี่ยวชาญการวิเคราะห์ข้อมูลพนักงาน 
        กรุณาวิเคราะห์และตอบคำถามต่อไปนี้โดยใช้ข้อมูลที่กำหนดให้:

        ข้อมูลที่มี:
        {data_context}

        คำถาม: {question}

        กรุณาตอบโดย:
        1. วิเคราะห์ข้อมูลที่เกี่ยวข้อง
        2. แสดงตัวเลขหรือสถิติประกอบ (ถ้ามี)
        3. ให้คำแนะนำหรือข้อเสนอแนะ (ถ้าเกี่ยวข้อง)"""

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการประมวลผล: {str(e)}"

def main():
    st.set_page_config(page_title="HR Analytics Dashboard", page_icon="📊", layout="wide")
    
    st.title("📊 HR Analytics Dashboard")
    st.write("ระบบวิเคราะห์ข้อมูล HR ด้วย AI")

    # Initialize Gemini
    model = initialize_gemini()
    
    # Load data
    data_dict = load_hr_data()
    
    if data_dict:
        # Sidebar for data selection
        with st.sidebar:
            st.header("เลือกข้อมูลที่ต้องการวิเคราะห์")
            selected_data = st.multiselect(
                "เลือกชุดข้อมูล:",
                list(data_dict.keys()),
                default=list(data_dict.keys())[0]
            )
            
            st.header("ข้อมูลที่มี")
            for data_name in selected_data:
                st.subheader(f"📁 {data_name}")
                st.write("Columns:", ", ".join(data_dict[data_name].columns.tolist()))
        
        # Main content
        tab1, tab2 = st.tabs(["📊 Data Explorer", "💬 AI Assistant"])
        
        with tab1:
            for data_name in selected_data:
                st.subheader(f"📊 {data_name}")
                st.dataframe(data_dict[data_name].head())
                
                # Basic statistics
                st.write("สถิติพื้นฐาน:")
                st.dataframe(data_dict[data_name].describe())
        
        with tab2:
            # Initialize chat history
            if "messages" not in st.session_state:
                st.session_state.messages = []
            
            # Display chat history
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            
            # Create data context for Gemini
            data_context = ""
            for data_name in selected_data:
                df = data_dict[data_name]
                data_context += f"\n{data_name}:\n"
                data_context += f"Columns: {', '.join(df.columns)}\n"
                for col in df.select_dtypes(include=['number']).columns:
                    data_context += f"{col} stats: Min={df[col].min()}, Max={df[col].max()}, Mean={df[col].mean():.2f}\n"
            
            # Chat input
            if prompt := st.chat_input("ถามคำถามเกี่ยวกับข้อมูล HR..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                if model:
                    response = get_gemini_response(model, prompt, data_context)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    with st.chat_message("assistant"):
                        st.markdown(response)
            
            # Reset button
            if st.button("ล้างประวัติการสนทนา"):
                st.session_state.messages = []
                st.experimental_rerun()
    
    else:
        st.error("ไม่สามารถโหลดข้อมูลได้ กรุณาตรวจสอบไฟล์ CSV")

if __name__ == "__main__":
    main()