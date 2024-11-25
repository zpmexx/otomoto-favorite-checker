def observed_table(data_dict):
    body = ""
    if not data_dict:
        body = "No auctions observed (check log file)."
    else:
        body += f"<h2>Number of followed auctions: {len(data_dict)}</h2>"
        body += """
        <table border="1" cellpadding="10" cellspacing="0" style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr>
                    <th style="text-align: center;">Name</th>
                    <th style="text-align: center;">Followed since</th>
                    <th style="text-align: center;">City</th>
                    <th style="text-align: center;">Price</th>
                </tr>
            </thead>
            <tbody>
        """

    # Dynamically generating table rows
        for link, data in data_dict.items():
            body += f"""
                <tr>
                    <td style="text-align: center;"><a href="{link}">{data['title']}</a></td>
                    <td style="text-align: center;">{data['followed_since']}</td>
                    <td style="text-align: center;">{data['city']}</td>
                    <td style="text-align: center;">{data['price']}</td>
                </tr>
            """
            
        # End of the table
        body += """
            </tbody>
        </table>
        """
    
def deleted_table(data_dict):
    body = ""
    if data_dict:
        body += "<h4>Auctions that have been deleted:</h4>"
        body += """
        <table border="1" cellpadding="10" cellspacing="0" style="width: 100%; border-collapse: collapse; background-color: red;">
            <thead>
                <tr style="background-color: #ff9999;">
                    <th style="text-align: center; color: white;">Name</th>
                    <th style="text-align: center; color: white;">Followed since</th>
                    <th style="text-align: center; color: white;">City</th>
                    <th style="text-align: center; color: white;">Price</th>
                </tr>
            </thead>
            <tbody>
        """

        # Dynamically generating table rows
        for link, data in data_dict.items():
            body += f"""
                <tr style="background-color: #ffcccc;">
                    <td style="text-align: center;"><a href="{link}" style="color: black;">{data['title']}</a></td>
                    <td style="text-align: center; color: black;">{data['followed_since']}</td>
                    <td style="text-align: center; color: black;">{data['city']}</td>
                    <td style="text-align: center; color: black;">{data['price']}</td>
                </tr>
            """
        # End of the table
        body += """
            </tbody>
        </table>"""