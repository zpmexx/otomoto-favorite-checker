def observed_table(data_dict):
    body = ""
    if not data_dict:
        body = "No auctions observed (check log file)."
    else:
        body += """
        <table border="1" cellpadding="10" cellspacing="0" style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr>
                    <th style="text-align: center;">Name</th>
                    <th style="text-align: center;">Followed since</th>
                    <th style="text-align: center;">City</th>
                    <th style="text-align: center;">Price</th>
                    <th style="text-align: center;">Mileage</th>
                    <th style="text-align: center;">Fuel type</th>
                    <th style="text-align: center;">Gearbox type</th>
                    <th style="text-align: center;">Car body type</th>
                    <th style="text-align: center;">Engine displacement</th>
                    <th style="text-align: center;">Horsepower</th>
                    <th style="text-align: center;">Year</th>
                    <th style="text-align: center;">Model</th>
                    
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
                    <td style="text-align: center;">{data['przebieg']}</td>
                    <td style="text-align: center;">{data['rodzaj_paliwa']}</td>
                    <td style="text-align: center;">{data['skrzynia_biegow']}</td>
                    <td style="text-align: center;">{data['typ_nadwozia']}</td>
                    <td style="text-align: center;">{data['pojemnosc_skokowa']}</td>
                    <td style="text-align: center;">{data['moc']}</td>
                    <td style="text-align: center;">{data['rok_produkcji']}</td>
                    <td style="text-align: center;">{data['model_pojazdu']}</td>
                </tr>
            """
            
        # End of the table
        body += """
            </tbody>
        </table>
        """
    return body

def deleted_table(data_dict):
    body = ''
    if not data_dict:
        body = "No deleted auctions (check log file)."
    else:
        body += """
        <table border="1" cellpadding="10" cellspacing="0" style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr>
                    <th style="text-align: center;">Name</th>
                    <th style="text-align: center;">City</th>
                    <th style="text-align: center;">Followed since</th>
                    <th style="text-align: center;">Ended date</th>
                    <th style="text-align: center;">Auction duration (days)</th>
                    <th style="text-align: center;">Price</th>
                    <th style="text-align: center;">Mileage</th>
                    <th style="text-align: center;">Fuel type</th>
                    <th style="text-align: center;">Gearbox type</th>
                    <th style="text-align: center;">Car body type</th>
                    <th style="text-align: center;">Engine displacement</th>
                    <th style="text-align: center;">Horsepower</th>
                    <th style="text-align: center;">Year</th>
                    <th style="text-align: center;">Model</th>
                </tr>
            </thead>
            <tbody>
        """
    
    # Dynamically generating table rows
    for link, data in data_dict.items():
        body += f"""
            <tr>
                <td style="text-align: center;">{data['title']}</td>
                <td style="text-align: center;">{data['city']}</td>
                <td style="text-align: center;">{data['followed_since']}</td>
                <td style="text-align: center;">{data['ended_date']}</td>
                <td style="text-align: center;">{data['duration']}</td>
                <td style="text-align: center;">{data['price']}</td>
                <td style="text-align: center;">{data['przebieg']}</td>
                <td style="text-align: center;">{data['rodzaj_paliwa']}</td>
                <td style="text-align: center;">{data['skrzynia_biegow']}</td>
                <td style="text-align: center;">{data['typ_nadwozia']}</td>
                <td style="text-align: center;">{data['pojemnosc_skokowa']}</td>
                <td style="text-align: center;">{data['moc']}</td>
                <td style="text-align: center;">{data['rok_produkcji']}</td>
                <td style="text-align: center;">{data['model_pojazdu']}</td>
            </tr>
        """
        
    # End of the table
    body += """
        </tbody>
    </table>
    """
    return body