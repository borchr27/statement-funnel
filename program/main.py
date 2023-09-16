from program.utils import (
	get_file_names, 
	import_data, 
	format_data,
	review_data,
	insert_data_to_file, 
	ACC_DEBIT, 
	ACC_CREDITCARD
)


def debug():
	print(ACC_DEBIT.origin_file_name)
	for i in range(5):
		print('\t', ACC_DEBIT.transactions[i].description)

	print(ACC_CREDITCARD.origin_file_name)
	for i in range(5):
		print('\t', ACC_CREDITCARD.transactions[i].description)


if __name__ == "__main__":
	file_names = get_file_names()
	import_data(file_names)
	format_data()
	review_data()
	insert_data_to_file()
