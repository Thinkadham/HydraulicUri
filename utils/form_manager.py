import streamlit as st
import hashlib

class FormManager:
    def __init__(self, page_name):
        self.page_name = page_name
        self.form_counter = 0
    
    def get_form_key(self, form_name):
        """Generate unique form key"""
        self.form_counter += 1
        base_key = f"{self.page_name}_{form_name}_{self.form_counter}"
        return hashlib.md5(base_key.encode()).hexdigest()[:10]
    
    def text_input(self, label, form_name, field_name, **kwargs):
        """Create text input with automatic key"""
        form_key = self.get_form_key(form_name)
        return st.text_input(label, key=f"{form_key}_{field_name}", **kwargs)
    
    def number_input(self, label, form_name, field_name, **kwargs):
        """Create number input with automatic key"""
        form_key = self.get_form_key(form_name)
        return st.number_input(label, key=f"{form_key}_{field_name}", **kwargs)
    
    def selectbox(self, label, form_name, field_name, options, **kwargs):
        """Create selectbox with automatic key"""
        form_key = self.get_form_key(form_name)
        return st.selectbox(label, options, key=f"{form_key}_{field_name}", **kwargs)
    
    def form(self, form_name, **kwargs):
        """Create form with automatic key"""
        form_key = self.get_form_key(form_name)
        return st.form(key=form_key, **kwargs)

def text_area(self, label, form_name, field_name, **kwargs):
    """Create text area with automatic key"""
    form_key = self.get_form_key(form_name)
    return st.text_area(label, key=f"{form_key}_{field_name}", **kwargs)

def radio(self, label, form_name, field_name, options, **kwargs):
    """Create radio buttons with automatic key"""
    form_key = self.get_form_key(form_name)
    return st.radio(label, options, key=f"{form_key}_{field_name}", **kwargs)

def date_input(self, label, form_name, field_name, **kwargs):
    """Create date input with automatic key"""
    form_key = self.get_form_key(form_name)
    return st.date_input(label, key=f"{form_key}_{field_name}", **kwargs)

def form_submit_button(self, form_name, label="Submit", **kwargs):
    """Create form submit button with automatic key"""
    form_key = self.get_form_key(form_name)
    return st.form_submit_button(label, key=f"{form_key}_submit", **kwargs)
