def value_error_handle(exctype, value, tb, deduction_result):
    deduction_result.add_error(str(value))
    deduction_result.to_json()