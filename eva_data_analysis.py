import pandas as pd
import matplotlib.pyplot as plt


def read_json_to_csv(input_json_file, output_csv_file='eva_data.csv'):
    """
    Reads a JSON file and saves it as a CSV file.
    
    Parameters:
    input_json_file (str): The path to the input JSON file.
    output_csv_file (str): The path to the output CSV file.
    """
    if input_json_file == '':
        input_json_file = 'eva_data.json'

    print(f'Reading JSON data file {input_json_file}')
    df = pd.read_json(input_json_file, convert_dates=['date'], encoding='ascii')
    df['eva'] = df['eva'].astype(float)
    df.dropna(
        axis=0,
        subset=['duration', 'date'],
        inplace=True)  # drop rows where either duration or date is null

    df.sort_values('date', inplace=True)

    print(f'Saving data to CSV file {output_csv_file}')
    df.to_csv(output_csv_file, index=False, encoding='utf-8')

    return df


def convert_duration_to_hours(df):
    """
    Convert EVA duration strings in the format HH:MM to decimal hours.
    """
    hrs = []
    # Create a list of decimal values for duration in hours
    for val in df['duration']:
        hour, minute = val.split(":")
        hrs.append(int(hour) + int(minute) / 60)
    df['duration_hours'] = hrs
    df = df.drop('duration', axis=1)

    return df


def wrangle_data(df, dur_out='duration_by_astronaut.csv'):
    """
    Cleans and transforms the EVA data for analysis.
    
    Parameters:
    data (DataFrame): The input DataFrame containing EVA data.
    dur_out (str): The path to the output CSV file for duration data.

    Returns:
    DataFrame: A cleaned and transformed DataFrame ready for analysis.
    """
    # TODO Descriptive comment: add an explanation of what the 3 lines below do
    subset = df.loc[:, ['crew', 'duration']]  # subset of data with only columns crew and duration
    subset.crew = subset.crew.str.split(';').apply(lambda x: [i for i in x if i.strip()])  # anonymous function that takes a list of crew members and returns a list with whitespace stripped from names and empty strings removed
    subset = subset.explode('crew')  # expand entries in a list-like column across multiple rows, making each element in the list a separate row and keeping/replicating values in other columns

    subset = convert_duration_to_hours(subset)
    subset = subset.groupby('crew').sum()

    # TODO Inputs: this should be a command-line argument, not hardcoded
    # dur_out = 'duration_by_astronaut.csv'
    print(f'Saving to CSV file {dur_out}')
    subset.to_csv(dur_out, index=True, encoding='utf-8')

    return subset


if __name__ == "__main__":
    print("--START--")

    input_json_file = input("Enter the input JSON file name: ")
    output_csv_file = input("Enter the output CSV file name for EVA data: ")
    dur_out = input("Enter the output CSV file name for duration data: ")
    img_file = input("Enter the output image file name for cumulative graph: ")

    data = read_json_to_csv(input_json_file, output_csv_file)
    data = convert_duration_to_hours(data)

    data['cumulative_time'] = data['duration_hours'].cumsum()

    if not img_file:
        img_file = 'cumulative_eva_graph.png'

    print(f'Plotting cumulative spacewalk duration and saving to {img_file}')
    plt.plot(data['date'], data['cumulative_time'], 'ko-')
    plt.xlabel('Year')
    plt.ylabel('Total time spent in space to date (hours)')
    plt.tight_layout()
    plt.savefig(img_file)
    plt.show()

    print("--END--")
