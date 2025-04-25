import streamlit as st
import hashlib

class FormManager:
    def __init__(self, page_name):
        self.page_name = page_name
        self.form_keys = {}  # Store form keys for consistency
    
    def get_form_key(self, form_name):
        """Generate consistent form key for all elements in the same form"""
        if form_name not in self.form_keys:
            base_key = f"{self.page_name}_{form_name}"
            self.form_keys[form_name] = hashlib.md5(base_key.encode()).hexdigest()[:10]
        return self.form_keys[form_name]
    
    def form(self, form_name, **kwargs):
        """Create form context"""
        form_key = self.get_form_key(form_name)
        return st.form(key=form_key, **kwargs)
    
    def form_submit_button(self, form_name, label="Submit", **kwargs):
        """Create form submit button"""
        form_key = self.get_form_key(form_name)
        return st.form_submit_button(label, key=f"{form_key}_submit", **kwargs)
    
    def text_input(self, label, form_name, field_name, **kwargs):
        """Create text input"""
        form_key = self.get_form_key(form_name)
        return st.text_input(label, key=f"{form_key}_{field_name}", **kwargs)
    
    def number_input(self, label, form_name, field_name, **kwargs):
        """Create number input"""
        form_key = self.get_form_key(form_name)
        return st.number_input(label, key=f"{form_key}_{field_name}", **kwargs)
    
    def selectbox(self, label, form_name, field_name, options, **kwargs):
        """Create selectbox"""
        form_key = self.get_form_key(form_name)
        return st.selectbox(label, options, key=f"{form_key}_{field_name}", **kwargs)
    
    def text_area(self, label, form_name, field_name, **kwargs):
        """Create text area"""
        form_key = self.get_form_key(form_name)
        return st.text_area(label, key=f"{form_key}_{field_name}", **kwargs)
    
    def date_input(self, label, form_name, field_name, **kwargs):
        """Create date input"""
        form_key = self.get_form_key(form_name)
        return st.date_input(label, key=f"{form_key}_{field_name}", **kwargs)
    
    def radio(self, label, form_name, field_name, options, **kwargs):
        """Create radio buttons"""
        form_key = self.get_form_key(form_name)
        return st.radio(label, options, key=f"{form_key}_{field_name}", **kwargs)
    
    def checkbox(self, label, form_name, field_name, **kwargs):
        """Create checkbox"""
        form_key = self.get_form_key(form_name)
        return st.checkbox(label, key=f"{form_key}_{field_name}", **kwargs)
    
    def slider(self, label, form_name, field_name, **kwargs):
        """Create slider"""
        form_key = self.get_form_key(form_name)
        return st.slider(label, key=f"{form_key}_{field_name}", **kwargs)
    
    def file_uploader(self, label, form_name, field_name, **kwargs):
        """Create file uploader"""
        form_key = self.get_form_key(form_name)
        return st.file_uploader(label, key=f"{form_key}_{field_name}", **kwargs)
    
    def time_input(self, label, form_name, field_name, **kwargs):
        """Create time input"""
        form_key = self.get_form_key(form_name)
        return st.time_input(label, key=f"{form_key}_{field_name}", **kwargs)
    
    def multiselect(self, label, form_name, field_name, options, **kwargs):
        """Create multiselect"""
        form_key = self.get_form_key(form_name)
        return st.multiselect(label, options, key=f"{form_key}_{field_name}", **kwargs)
