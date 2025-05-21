#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 15 07:40:01 2025

@author: reineepanjabi
"""

import os
import pandas as pd
import numpy as np
# File paths
USERS_FILE = 'data/users.csv'
EXPENSES_FILE = 'data/expenses.csv'

def load_user_data():
    """Load user data from CSV file or create empty dataframe if file doesn't exist"""
    if os.path.exists(USERS_FILE):
        return pd.read_csv(USERS_FILE)
    else:
        # Create empty dataframe with required columns
        columns = [
            "Name", "Password", "Age", "Gender", "Student_Accommodation",
            "Utilities", "Grocery_shopping", "Takeaways/dining",
            "Public_Transportation", "Tuition_Fees", "Books_and_Supplies",
            "Clothing", "Entertainment", "Health/Medical_Expenses", "Monthly_Income"
        ]
        return pd.DataFrame(columns=columns)

def save_user_data(users_df):
    """Save user data to CSV file"""
    users_df.to_csv(USERS_FILE, index=False)

def load_expense_data():
    """Load expense data from CSV file or create empty dataframe if file doesn't exist"""
    if os.path.exists(EXPENSES_FILE):
        return pd.read_csv(EXPENSES_FILE)
    else:
        # Create empty dataframe with required columns
        columns = ["Username", "Category", "Amount", "Date", "Note"]
        return pd.DataFrame(columns=columns)

def save_expense_data(expenses_df):
    """Save expense data to CSV file"""
    expenses_df.to_csv(EXPENSES_FILE, index=False)

def get_user_expenses(expenses_df, username):
    """Get expenses for a specific user"""
    return expenses_df[expenses_df['Username'] == username].copy()

def calculate_expense_metrics(user_data, user_expenses):
    """Calculate expense metrics for dashboard"""
    # Calculate total expenses from user expenses
    if user_expenses.empty:
        total_expenses = 0
        expense_by_category = pd.DataFrame(columns=['Category', 'Amount'])
    else:
        total_expenses = user_expenses['Amount'].sum()
        expense_by_category = user_expenses.groupby('Category')['Amount'].sum().reset_index()
   
    # Get income
    income = user_data['Monthly_Income']
   
    # Calculate savings
    savings = income - total_expenses
   
    # Calculate expense ratio (% of income spent)
    expense_ratio = (total_expenses / income * 100) if income > 0 else 0
   
    return total_expenses, expense_by_category, income, savings, expense_ratio

def generate_optimization_tips(user_data, user_expenses):
    """Generate budget optimization tips based on user data and expenses"""
    tips = {}
   
    # Calculate total expenses
    total_expenses = user_expenses['Amount'].sum() if not user_expenses.empty else 0
    income = user_data['Monthly_Income']
   
    # Housing tips
    accommodation_cost = user_data['Student_Accommodation']
    if accommodation_cost > 0:
        housing_ratio = accommodation_cost / income if income > 0 else 0
        tips['Housing'] = []
       
        if housing_ratio > 0.4:
            tips['Housing'].append("Your housing costs exceed 40% of your income. Consider finding roommates or cheaper accommodation.")
   
   
    # Food tips
    grocery_cost = user_data['Grocery_shopping']
    dining_cost = user_data['Takeaways/dining']
    food_cost = grocery_cost + dining_cost
   
    if food_cost > 0:
        food_ratio = food_cost / income if income > 0 else 0
        dining_ratio = dining_cost / food_cost if food_cost > 0 else 0
       
        tips['Food'] = []
       
        if food_ratio > 0.15:
            tips['Food'].append("Your food expenses are higher than recommended. Try meal planning to reduce costs.")
       
        if dining_ratio > 0.5:
            tips['Food'].append("You're spending more on takeaways/dining than groceries. Cook at home more often to save money.")
       
       
       
   
    # Transportation tips
    transport_cost = user_data['Public_Transportation']
    if transport_cost > 0:
        transport_ratio = transport_cost / income if income > 0 else 0
       
        tips['Transportation'] = []
       
        if transport_ratio > 0.1:
            tips['Transportation'].append("Your transportation costs are high. Look into student discount passes or carpooling.")
   
   
    # Entertainment tips
    entertainment_cost = user_data['Entertainment']
    if entertainment_cost > 0:
        entertainment_ratio = entertainment_cost / income if income > 0 else 0
       
        tips['Entertainment'] = []
       
        if entertainment_ratio > 0.1:
            tips['Entertainment'].append("Your entertainment spending is high. Look for free campus events and student discounts.")
       
   
    # General savings tips
    if income > 0:
        savings_rate = (income - total_expenses) / income
       
        tips['Savings'] = []
       
        if savings_rate < 0.1:
            tips['Savings'].append("You're saving less than 10% of your income. Try to increase this to build an emergency fund.")
       
   
   
    return tips