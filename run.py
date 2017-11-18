import click
import csv
import cryptocompare
import pprint

@click.command()
@click.option('--file', default='results.csv', help='File name to save to.')
def get(file):
    data = cryptocompare.get_coin_list(format=False)
    save_csv(data.values(), file)


def save_csv(data, file):
    with open(file, 'w') as csv_file:
        wr = csv.writer(csv_file, delimiter=',')
        # write header
        first = next (iter (data))
        wr.writerow(list(first.keys()))
        for row in data:
            wr.writerow(list(row.values()))

if __name__ == '__main__':
    get()