import streamlit as st
import pandas as pd
import google.generativeai as genai
from datetime import datetime

# Initialize Gemini API
def initialize_gemini():
    genai.configure(api_key="AIzaSyCCQumrGPGSzDgY7_YFSSI5kFzYb-WXFB4")
    return genai.GenerativeModel('gemini-pro')

# Load CSV data
def load_hr_data():
    try:
        employee_data = pd.read_csv('employee_data_1511.csv')
        employee_skills = pd.read_csv('employee_skills_1511.csv')
        
        # Handle missing or empty feedback data
        try:
            feedback_data = pd.read_csv('feedback_data_page.csv')
            if feedback_data.empty:
                feedback_data = pd.DataFrame(columns=['Feedback', 'Timestamp'])
        except Exception as e:
            feedback_data = pd.DataFrame(columns=['Feedback', 'Timestamp'])  # Default empty dataframe with headers
            st.warning(f"Could not load feedback data: {str(e)}")

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

# Function to get data insights using Gemini model
def get_data_insights(model, data_dict, selected_data):
    insights = {}
    for data_name in selected_data:
        df = data_dict[data_name]
        prompt = f"""คุณเป็น HR Analyst ที่เชี่ยวชาญการวิเคราะห์ข้อมูลพนักงาน 
        กรุณาวิเคราะห์ข้อมูลต่อไปนี้และให้ข้อมูลเชิงลึกที่สำคัญ:

        ชุดข้อมูล: {data_name}
        Columns: {', '.join(df.columns)}
        
        สำหรับคอลัมน์ตัวเลข:
        {', '.join([f"{col}: Min={df[col].min()}, Max={df[col].max()}, Mean={df[col].mean():.2f}" for col in df.select_dtypes(include=['number']).columns])}

        กรุณาให้:
        1. ข้อมูลเชิงลึก 3-4 ประเด็นที่สำคัญ
        2. แนวโน้มหรือรูปแบบที่น่าสนใจ
        3. ข้อเสนอแนะสำหรับ HR"""

        try:
            response = model.generate_content(prompt)
            insights[data_name] = response.text
        except Exception as e:
            insights[data_name] = f"ไม่สามารถวิเคราะห์ข้อมูลได้: {str(e)}"
    
    return insights

# Function to get Gemini's response based on user input
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

# Function to save feedback from employee with timestamp
# Function to save feedback along with Employee_ID
def save_feedback(feedback, feedback_type="general"):
    try:
        feedback_data = pd.read_csv('feedback_data_page.csv')  # Updated file name
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_feedback = pd.DataFrame([{
            'Employee_ID': st.session_state.employee_id,  # Link feedback to the user
            'Feedback': feedback, 
            'Timestamp': timestamp,
            'Feedback_Type': feedback_type  # Add a type for feedback (e.g., AI Interaction, Emotional State)
        }])
        feedback_data = pd.concat([feedback_data, new_feedback], ignore_index=True)
        feedback_data.to_csv('feedback_data_page.csv', index=False)
        st.success("Feedback ได้รับการบันทึกแล้ว")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการบันทึก Feedback: {str(e)}")

# Logout function to clear session
def logout():
    st.session_state.clear()  # Clear the session state
    st.success("คุณได้ออกจากระบบแล้ว")
    st.experimental_rerun()  # Reload the app to show the login page

def login_page():
    st.title("เข้าสู่ระบบ")
    
    # Create login form
    employee_id = st.text_input("Employee ID")  # New field
    username = st.text_input("ชื่อผู้ใช้")
    password = st.text_input("รหัสผ่าน", type="password")
    
    if st.button("เข้าสู่ระบบ"):
        # Simulate user authentication (replace this with real database or API check)
        user_database = {
            "101": {"username": "admin", "password": "password123", "role": "HR"},
            "102": {"username": "user1", "password": "user123", "role": "พนักงาน"}
        }
        
        if employee_id in user_database:
            user = user_database[employee_id]
            if username == user["username"] and password == user["password"]:
                st.session_state.logged_in = True
                st.session_state.employee_id = employee_id
                st.session_state.username = username
                st.session_state.role = user["role"]
                st.rerun()  # Reload the app without rendering additional UI elements
            else:
                st.error("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
        else:
            st.error("ไม่พบ Employee ID นี้ในระบบ")
def display_example_questions():
    st.subheader("ตัวอย่างคำถามที่คุณสามารถถาม AI ได้:")
    example_questions = [
        "การลาหยุดของพนักงานคนนี้เป็นอย่างไร?",
        "พนักงานคนนี้มาสายบ่อยไหม?",
        "ข้อมูลวันลาในปีนี้มีแนวโน้มอย่างไร?",
        "สามารถบอกสถิติการขาดงานของพนักงานคนนี้ได้ไหม?"
    ]
    return st.selectbox("เลือกคำถามจากตัวเลือก", example_questions)
# Main Streamlit app function
def main():
    st.set_page_config(page_title="HR Analytics Dashboard", page_icon="📊", layout="wide")
    
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        login_page()  # Show login page if not logged in
    else:
        st.title("📊 HR Analytics Dashboard")
        st.write("ระบบวิเคราะห์ข้อมูล HR ด้วย AI")
        
        # Initialize Gemini
        model = initialize_gemini()
        
        # Load data
        data_dict = load_hr_data()
        
        if data_dict:
            # Sidebar for user role selection
            with st.sidebar:
                st.header(f"Welcome, {st.session_state.username}")
                st.write(f"Employee ID: {st.session_state.employee_id}")
                st.write(f"บทบาทของคุณ: {st.session_state.role}")

                if st.session_state.role == "HR":
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
                
                if st.button("ออกจากระบบ"):
                    logout()  # Logout button

            if st.session_state.role == "พนักงาน":
                tab1, tab2 = st.tabs(["💬 ส่ง Feedback", "🤖 AI Assistant"])
                
                with tab1:
                    st.header("กรุณากรอก Feedback")
                    feedback = st.text_area("กรอก Feedback ของคุณที่นี่")
                    if st.button("ส่ง Feedback"):
                        if feedback:
                            save_feedback(feedback)
                        else:
                            st.warning("กรุณากรอกข้อความก่อนส่ง")
                
                with tab2:
                    # Display example questions for the employee
                    st.subheader("ตัวอย่างคำถามที่คุณสามารถถาม AI ได้:")
                    example_questions = [
                        "การลาหยุดของพนักงานคนนี้เป็นอย่างไร?",
                        "พนักงานคนนี้มาสายบ่อยไหม?",
                        "ข้อมูลวันลาในปีนี้มีแนวโน้มอย่างไร?",
                        "สามารถบอกสถิติการขาดงานของพนักงานคนนี้ได้ไหม?"
                    ]
                    selected_question = st.selectbox("เลือกคำถามจากตัวเลือก", example_questions)

                    # Initialize chat history for Employees
                    if "employee_messages" not in st.session_state:
                        st.session_state.employee_messages = []

                    # Display chat history
                    for message in st.session_state.employee_messages:
                        with st.chat_message(message["role"]):
                            st.markdown(message["content"])

                    # Chat input
                    if prompt := st.chat_input(f"ถามคำถามเกี่ยวกับข้อมูลบริษัทหรือข้อมูลทั่วไป... หรือเลือกจากตัวเลือกด้านบน: {selected_question}"):
                        st.session_state.employee_messages.append({"role": "user", "content": prompt})
                        with st.chat_message("user"):
                            st.markdown(prompt)

                        if model:
                            # Simple response generation for employees
                            try:
                                response = model.generate_content(
                                    f"""คุณเป็น AI Assistant ที่ช่วยตอบคำถามพนักงาน:
                                    คำถาม: {prompt}
                                    กรุณาตอบอย่างสุภาพและให้ข้อมูลที่เหมาะสม"""
                                ).text
                                st.session_state.employee_messages.append({"role": "assistant", "content": response})
                                with st.chat_message("assistant"):
                                    st.markdown(response)
                                
                                # Ask for feedback after the AI response
                                feedback_prompt = "หลังจากที่ได้รับคำตอบจาก AI, คุณรู้สึกอย่างไร? ช่วยให้ความช่วยเหลือได้ดีหรือไม่? กรุณากรอกความคิดเห็นของคุณ"
                                feedback = st.text_area(feedback_prompt)
                                if st.button("ส่ง Feedback"):
                                    save_feedback(feedback, feedback_type="AI Interaction")
                            except Exception as e:
                                st.error(f"เกิดข้อผิดพลาดในการประมวลผลคำตอบ: {str(e)}")

if __name__ == "__main__":
    main()

