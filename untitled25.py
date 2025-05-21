
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
from utils import (
    load_user_data, save_user_data,
    load_expense_data, save_expense_data,
    get_user_expenses,
    calculate_expense_metrics
)

# Set page configuration
st.set_page_config(
    page_title="Student Budget Tracker",page_icon="💸",
    layout="wide"
)

# Initialize session states
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'show_registration' not in st.session_state:
    st.session_state.show_registration = False

# Load user data
users_df = load_user_data()
expenses_df = load_expense_data()

def authenticate_user(username, password):
    """Authenticate a user based on username and password"""
    if username in users_df['Name'].values:
        user_row = users_df[users_df['Name'] == username].iloc[0]
        # Convert password for comparison - CSV stores integers as numeric
        stored_pass = str(user_row['Password'])
        if stored_pass == password:  
            st.session_state.authenticated = True
            st.session_state.current_user = username
            return True
    return False

def register_user(user_data):
    """Register a new user with the provided data"""
    global users_df
   
    # to Check if user already exists
    if user_data['Name'] in users_df['Name'].values:
        return False, "Username already exists!"
   
    # Adding user to dataframe
    users_df = pd.concat([users_df, pd.DataFrame([user_data])])
    save_user_data(users_df)
   
    # Set session state
    st.session_state.authenticated = True
    st.session_state.current_user = user_data['Name']
    st.session_state.show_registration = False
       
    return True,print("Registration successful!")
   

def add_expense(expense_data):
   
    global expenses_df
   
    # Adding expense to dataframe
    expense_data['Username'] = st.session_state.current_user
    expense_data['Date'] = datetime.datetime.now().strftime('%Y-%m-%d')
   
    expenses_df = pd.concat([expenses_df, pd.DataFrame([expense_data])])
    save_expense_data(expenses_df)
   
    return True

def show_login_page():
    """Display the login page"""
    st.title("Student Budget Tracker")
   
    col1, col2 = st.columns(2)
   
    with col1:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
       
        if st.button("Login"):
            if authenticate_user(username, password):
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
   
    with col2:
        st.subheader("New User?")
        if st.button("Register"):
            st.session_state.show_registration = True
            st.rerun()

def show_registration_page():
    """Display the registration page"""
    global expenses_df  
    st.title("Registration Form")
   
    with st.form("registration_form"):
        name = st.text_input("Name")
        password = st.text_input("Password", type="password")
        age = st.number_input("Age", min_value=16, max_value=100, step=1)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
       
        st.subheader("Monthly Expenses (in ₹)")
        accommodation = st.number_input("Student Accommodation", min_value=0, step=10)
        utilities = st.number_input("Utilities", min_value=0, step=10)
        grocery = st.number_input("Grocery Shopping", min_value=0, step=10)
        dining = st.number_input("Takeaways/Dining", min_value=0, step=10)
        transportation = st.number_input("Public Transportation", min_value=0, step=10)
        tuition = st.number_input("Tuition Fees", min_value=0, step=100)
        books = st.number_input("Books and Supplies", min_value=0, step=10)
        clothing = st.number_input("Clothing", min_value=0, step=10)
        entertainment = st.number_input("Entertainment", min_value=0, step=10)
        health = st.number_input("Health/Medical Expenses", min_value=0, step=10)
        monthly_income = st.number_input("Monthly Income", min_value=0, step=100)
       
        submitted = st.form_submit_button("Register")
       
        if submitted:
            user_data = {
                "Name": name,
                "Password": password,  
                "Age": age,
                "Gender": gender,
                "Student_Accommodation": accommodation,
                "Utilities": utilities,
                "Grocery_shopping": grocery,
                "Takeaways/dining": dining,
                "Public_Transportation": transportation,
                "Tuition_Fees": tuition,
                "Books_and_Supplies": books,
                "Clothing": clothing,
                "Entertainment": entertainment,
                "Health/Medical_Expenses": health,
                "Monthly_Income": monthly_income
            }
           
            # Adding initial expenses
            for category in ["Student_Accommodation", "Utilities", "Grocery_shopping",
                            "Takeaways/dining", "Public_Transportation", "Tuition_Fees",
                            "Books_and_Supplies", "Clothing", "Entertainment", "Health/Medical_Expenses"]:
                if user_data[category] > 0:
                    expense_data = {
                        "Username": name,
                        "Category": category,
                        "Amount": user_data[category],
                        "Date": datetime.datetime.now().strftime('%Y-%m-%d')
                    }
                    expenses_df = pd.concat([expenses_df, pd.DataFrame([expense_data])], ignore_index=True)
           
            save_expense_data(expenses_df)
           
            success, message = register_user(user_data)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
   
    if st.button("Back to Login"):
        st.session_state.show_registration = False
        st.rerun()

def show_dashboard():
   
    st.title(f"Welcome, {st.session_state.current_user}!")
   
    # Getting user data
    user_data = users_df[users_df['Name'] == st.session_state.current_user].iloc[0]
    user_expenses = get_user_expenses(expenses_df, st.session_state.current_user)
   
    # Sidebar menu
    st.sidebar.title(":red[Menu]")
    # Initializing sidebar_option in session_state if it doesn't exist
    if 'sidebar_option' not in st.session_state:
        st.session_state.sidebar_option = "Dashboard"
   
    # Sidebar options
    sidebar_option = st.sidebar.radio(
        "Navigate",
        ["Dashboard", "About Student Spending", "About This App"]
    )
    st.session_state.sidebar_option = sidebar_option
   
    # Logout button
    if st.sidebar.button(":red[Logout]"):
        st.session_state.authenticated = False
        st.session_state.current_user = None
        st.rerun()
   
    # Show content based on sidebar selection
    if sidebar_option == "Dashboard":
        # Dashboard tabs
        tab1, tab2, tab3 = st.tabs(["Expense Analysis", "Optimization Tips", "Add Expenses"])
       
        # Tab 1: Expense Analysis
        with tab1:
            st.header(":blue[Expense Analysis]")
           
            # Calculate metrics
            total_expenses, expense_by_category, income, savings, expense_ratio = calculate_expense_metrics(
                user_data, user_expenses
            )
           
            # Display key metrics
            col1, col2, col3, col4 = st.columns(4)
           
            with col1:
                st.metric("Total Monthly Expenses", f"₹{int(total_expenses)}")
           
            with col2:
                st.metric("Monthly Income", f"₹{int(income)}")
           
            with col3:
                st.metric("Monthly Savings", f"₹{int(savings)}")
           
            with col4:
                st.metric("Expense Ratio", f"{expense_ratio:.2f}%")
           
            # Expense breakdown charts
            st.subheader(":violet[Expense Breakdown]")
           
            col1, col2 = st.columns(2)
           
            with col1:
                # Pie chart
                if not expense_by_category.empty:
                    fig, ax = plt.subplots(figsize=(8, 8))
                    ax.pie(expense_by_category['Amount'], labels=expense_by_category['Category'], autopct='%1.1f%%')
                    ax.set_title('Expenses by Category')
                    st.pyplot(fig)
                   
                else:
                    st.info("No expense data available.")
           
            with col2:
                # Bar chart
                if not expense_by_category.empty:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    colors = plt.cm.viridis(np.linspace(0, 1, len(expense_by_category)))
                    bars = ax.bar(expense_by_category['Category'], expense_by_category['Amount'],color=colors)
                    ax.set_title('Expenses by Category')
                    ax.set_xlabel('Category')
                    ax.set_ylabel('Amount (₹)')
                    plt.xticks(rotation=45, ha='right')
                    plt.tight_layout()
                    st.pyplot(fig)
                else:
                    st.info("No expense data available.")
           
        # Tab 2: Optimization Tips
        with tab2:
            st.subheader(":blue[General Budgeting Guidelines for Students]")
           
            st.write("""
            ### :violet[50/30/20 Rule]
            - **50%** of income for necessities (rent, groceries, utilities)
            - **30%** for wants (dining out, entertainment)
            - **20%** for savings and debt repayment
           
           
            ### :violet[Build an Emergency Fund]
            - Aim to save 3-6 months of essential expenses
            - Start small if needed - even $10-20 per week adds up
           
            ### :violet[ Reduce Recurring Expenses]
            - Share subscriptions with roommates
            - Look for student discounts
            """)
       
        # Tab 3: Add Expenses
        with tab3:
            st.header(":blue[Add New Expense]")
           
            with st.form("expense_form"):
                category = st.selectbox(
                    "Expense Category",
                    ["Student_Accommodation", "Utilities", "Grocery_shopping",
                     "Takeaways/dining", "Public_Transportation", "Tuition_Fees",
                     "Books_and_Supplies", "Clothing", "Entertainment", "Health/Medical_Expenses", "Other"]
                )
               
                if category == "Other":
                    category = st.text_input("Specify Category")
               
                amount = st.number_input("Amount ($)", min_value=0.01, step=1.0)
                date = st.date_input("Date", datetime.datetime.now())
                note = st.text_area("Note (Optional)")
               
                submitted = st.form_submit_button("Add Expense")
               
                if submitted:
                    expense_data = {
                        "Username": st.session_state.current_user,
                        "Category": category,
                        "Amount": amount,
                        "Date": date.strftime('%Y-%m-%d'),
                        "Note": note
                    }
                   
                    if add_expense(expense_data):
                        st.success("Expense added successfully!")
                        # Update user data with new expense
                        if category in user_data:
                            users_df.loc[users_df['Name'] == st.session_state.current_user, category] += amount
                            save_user_data(users_df)
                        st.rerun()
                    else:
                        st.error("Failed to add expense. Please try again.")
   
    elif sidebar_option == "About Student Spending":
        st.header(":blue[Average Student Spending Statistics]")
       
        # Calculate average spending from all users
        st.subheader(":violet[Average Monthly Expenses for College Students]")
       
        # Display average spending data
        if len(users_df) > 0:
            expense_categories = [
                "Student_Accommodation", "Utilities", "Grocery_shopping",
                "Takeaways/dining", "Public_Transportation", "Tuition_Fees",
                "Books_and_Supplies", "Clothing", "Entertainment", "Health/Medical_Expenses"
            ]
           
            avg_expenses = {}
            for category in expense_categories:
                avg_expenses[category] = users_df[category].mean()
           
            # Create a dataframe for visualization
            avg_expense_df = pd.DataFrame(list(avg_expenses.items()), columns=['Category', 'Average Amount'])
           
            # Display data in a table
            st.dataframe(avg_expense_df, use_container_width=True)
           
            # Bar chart for average expenses
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(avg_expense_df['Category'], avg_expense_df['Average Amount'],color="teal")
            ax.set_title('Average Student Expenses by Category')
            ax.set_xlabel('Category')
            ax.set_ylabel('Amount ($)')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig)
           
            # Show how user compares to average
            st.subheader(":violet[Comaprison with Average]")
           
            comparison_data = []
            for category in expense_categories:
                user_amount = user_data[category]
                avg_amount = avg_expenses[category]
                diff_percent = ((user_amount - avg_amount) / avg_amount * 100) if avg_amount > 0 else 0
                comparison_data.append({
                    'Category': category,
                    'Your Spending': user_amount,
                    'Average': avg_amount,
                    'Difference %': diff_percent
                })
           
            comparison_df = pd.DataFrame(comparison_data)
            st.dataframe(comparison_df, use_container_width=True)
        else:
            st.info("Not enough data to calculate average student spending.")
       
        # National statistics
       
        st.write("""
        ### :violet[National Averages for Student Spending (2023-2024)]
       
        - **Housing**: $7,500 - $12,000 per year
        - **Food**: $2,500 - $4,500 per year
        - **Textbooks & Supplies**: $1,000 - $1,500 per year
        - **Transportation**: $1,000 - $1,800 per year
        - **Personal Expenses**: $1,500 - $3,000 per year
       
        *Source: National Association of College and University Business Officers*
        """)
       
    elif sidebar_option == "About This App":
        st.header(":blue[About Student Budget Tracker]")
       
        st.write("""
        ### :violet[ Purpose of This App]
       
        The Student Budget Tracker is designed to help students manage their finances effectively during their
        academic journey. By tracking expenses, analyzing spending patterns, and providing personalized optimization
        tips, this application aims to promote financial literacy and healthy money management habits among students.
       
        ### :violet[ Features]
       
        - **Expense Tracking**: Log and categorize your expenses easily
        - **Visual Analytics**: Visualize your spending patterns with interactive charts
        - **Budget Optimization**: Receive personalized tips based on your spending habits
        - **Spending Comparison**: See how your expenses compare to averages
       
       
        ### :violet[ How to Use This App]
       
        1. **Register/Login**: Create an account or log in with your credentials
        2. **Track Expenses**: Add your expenses in the "Add Expenses" tab
        3. **Analyze Spending**: View your spending patterns in the "Expense Analysis" tab
        4. **Get Tips**: Find personalized budget optimization advice in the "Optimization Tips" tab
        5. **Compare**: Check how your spending compares to other students
       """)
       
       

# Main application flow
def main():
    if st.session_state.authenticated:
        show_dashboard()
    elif st.session_state.show_registration:
        show_registration_page()
    else:
        show_login_page()

if __name__ == "__main__":
    main()

