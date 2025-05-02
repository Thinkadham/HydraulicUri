import streamlit as st
# Import necessary functions, including the new ones
from utils.db import add_user, get_users, update_user_permissions, get_user_by_username
import hashlib # For password hashing
import pandas as pd # For better table display

# Define all available pages (excluding User Management itself for selection)
# Ensure these names match exactly what's used in app.py navigation/routing
ALL_AVAILABLE_PAGES = ["Dashboard", "Create Bill", "Contractors", "Works", "Reports", "Settings"]

def show_user_management():
    """Displays the user management page content."""
    st.title("User Management")
    st.write("This page will allow administrators to create and manage users.")

    # --- Create New User Section ---
    st.subheader("Create New User")
    with st.form("create_user_form", clear_on_submit=True):
        new_username = st.text_input("Username", key="new_user_username")
        new_password = st.text_input("Password", type="password", key="new_user_password")
        new_role = st.selectbox("Role", ["admin", "restricted"], key="new_user_role")
        submitted = st.form_submit_button("Create User")

        if submitted:
            if not new_username or not new_password:
                st.warning("Username and Password cannot be empty.")
            else:
                # Hash the password before storing
                hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
                try:
                    # Pass role to add_user, default permissions are handled inside
                    result = add_user(new_username, hashed_password, new_role)
                    if result: # Check if DB operation was successful
                         st.success(f"User '{new_username}' created successfully with role '{new_role}'.")
                         st.rerun() # Rerun to update the user list
                    else:
                         st.error(f"Failed to create user '{new_username}'. Check logs or database.")
                except Exception as e:
                    # Catch potential exceptions like duplicate username if DB constraint exists
                    st.error(f"Failed to create user: {e}")

    st.markdown("---") # Separator

    # --- Existing Users Section ---
    st.subheader("Manage Existing Users & Permissions")
    try:
        # Fetch all user data needed (username, role, allowed_pages)
        # Note: get_users() currently only returns username, role. We need full data.
        # Let's modify this to fetch all data or use get_user_by_username iteratively (less efficient)
        # Option 1: Modify get_users() - Preferred (Requires changing get_users in db.py)
        # Option 2: Fetch details per user (shown below for now, less ideal for many users)

        all_users_basic = get_users() # Gets username, role

        if all_users_basic:
            user_details_list = []
            for basic_user in all_users_basic:
                # Fetch full details for each user to get allowed_pages
                full_user_data = get_user_by_username(basic_user['username'])
                if full_user_data:
                    user_details_list.append(full_user_data[0]) # get_user_by_username returns a list

            if user_details_list:
                # Use columns for layout
                col1, col2, col3 = st.columns([1, 2, 1]) # Adjust ratios as needed
                col1.markdown("**Username**")
                col2.markdown("**Role & Allowed Pages**")
                col3.markdown("**Actions**")

                for user in user_details_list:
                    username = user['username']
                    role = user['role']
                    # Ensure allowed_pages is a list, default to empty list if None/null from DB
                    current_allowed_pages = user.get('allowed_pages') or []

                    with st.container(): # Group elements for each user
                        c1, c2, c3 = st.columns([1, 2, 1])
                        c1.write(username)

                        if role == 'admin':
                            c2.markdown(f"**Role:** Admin (Full Access)")
                        else: # Restricted user
                            c2.markdown(f"**Role:** Restricted")
                            # Use a unique key for each multiselect based on username
                            selected_pages = c2.multiselect(
                                f"Allowed Pages for {username}",
                                options=ALL_AVAILABLE_PAGES,
                                default=current_allowed_pages,
                                key=f"pages_{username}",
                                label_visibility="collapsed" # Hide label above multiselect
                            )

                            # Save button for permissions change
                            if c3.button("Save Permissions", key=f"save_{username}"):
                                try:
                                    update_user_permissions(username, selected_pages)
                                    st.success(f"Permissions updated for {username}.")
                                    # No rerun needed here unless you want immediate visual confirmation
                                    # which might reset other interactions. Consider feedback carefully.
                                except Exception as e:
                                    st.error(f"Failed to update permissions for {username}: {e}")
                        st.markdown("---") # Separator between users
            else:
                 st.info("Could not retrieve full user details.")

        else:
            st.info("No users found.")
    except Exception as e:
        st.error(f"Failed to load users: {e}")
        st.exception(e) # Show full traceback in UI for debugging
