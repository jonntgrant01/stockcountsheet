                        # Product information with accessibility enhancements
                        with col1:
                            if st.session_state.accessibility_mode:
                                # High contrast version with ARIA attributes
                                st.markdown(accessible_html(
                                    "div", 
                                    f"<strong style='color:{get_theme_color('text')}; font-size: larger;'>Product ID:</strong> " + 
                                    f"<span style='color:{get_theme_color('text')};'>{row['product_id']}</span>",
                                    role="text", 
                                    aria_label=f"Product ID: {row['product_id']}"
                                ), unsafe_allow_html=True)
                                
                                st.markdown(accessible_html(
                                    "div", 
                                    f"<strong style='color:{get_theme_color('text')}; font-size: larger;'>Brand:</strong> " + 
                                    f"<span style='color:{get_theme_color('text')};'>{row['brand']}</span>",
                                    role="text", 
                                    aria_label=f"Brand: {row['brand']}"
                                ), unsafe_allow_html=True)
                                
                                st.markdown(accessible_html(
                                    "div", 
                                    f"<strong style='color:{get_theme_color('text')}; font-size: larger;'>Description:</strong> " + 
                                    f"<span style='color:{get_theme_color('text')};'>{row['description']}</span>",
                                    role="text", 
                                    aria_label=f"Description: {row['description']}"
                                ), unsafe_allow_html=True)
                                
                                st.markdown(accessible_html(
                                    "div", 
                                    f"<strong style='color:{get_theme_color('text')}; font-size: larger;'>Location:</strong> " + 
                                    f"<span style='color:{get_theme_color('text')};'>{row['location']}</span>",
                                    role="text", 
                                    aria_label=f"Location: {row['location']}"
                                ), unsafe_allow_html=True)
                                
                                st.markdown(accessible_html(
                                    "div", 
                                    f"<strong style='color:{get_theme_color('text')}; font-size: larger;'>Expected Count:</strong> " + 
                                    f"<span style='color:{get_theme_color('text')};'>{row['expected_count']}</span>",
                                    role="text", 
                                    aria_label=f"Expected Count: {row['expected_count']}"
                                ), unsafe_allow_html=True)
                            else:
                                # Standard version
                                st.markdown(f"**Product ID:** {row['product_id']}")
                                st.markdown(f"**Brand:** {row['brand']}")
                                st.markdown(f"**Description:** {row['description']}")
                                st.markdown(f"**Location:** {row['location']}")
                                st.markdown(f"**Expected Count:** {row['expected_count']}")