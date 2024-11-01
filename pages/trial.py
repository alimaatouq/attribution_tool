def aggregate_spend(df, consolidated_df):
    spend_data = []

    # Group consolidated spend columns by channel and creative
    for consolidated_name in consolidated_df['Consolidated Column Name'].unique():
        # Extract channel and creative from the consolidated column name
        match = re.match(r'([A-Za-z]+)_([A-Za-z]+)', consolidated_name)
        if match:
            channel = match.group(1)
            creative = match.group(2)
            
            # Sum up all original columns that match this consolidated name pattern
            matching_columns = [col for col in df.columns if re.sub(r'([_-]\d+)', '', col) == consolidated_name]
            spend_sum = df[matching_columns].sum(axis=1).sum()  # Sum across rows and then total
            
            # Append to spend_data list
            spend_data.append({'Channel': channel, 'Creative': creative, 'Spend': spend_sum})

    # Convert spend data to DataFrame
    spend_df = pd.DataFrame(spend_data)

    # Calculate total spend
    total_spend = spend_df['Spend'].sum()
    spend_df['Percentage Contribution'] = (spend_df['Spend'] / total_spend) * 100

    # Add total row to DataFrame
    total_row = pd.DataFrame([{
        'Channel': 'Total',
        'Creative': '',
        'Spend': total_spend,
        'Percentage Contribution': 100.0
    }])
    spend_df = pd.concat([spend_df, total_row], ignore_index=True)
    
    return spend_df
