import re

def is_valid_cpf(cpf: str) -> bool:
    cpf = re.sub(r'\D', '', cpf)
    if len(cpf) != 11:
        return False
    
    # Check for all same digits (e.g., 111.111.111-11)
    if cpf == cpf[0] * 11:
        return False

    # Calculate first verification digit
    sum_digits = sum(int(cpf[i]) * (10 - i) for i in range(9))
    expected_digit_1 = (sum_digits * 10 % 11) % 10
    if int(cpf[9]) != expected_digit_1:
        return False

    # Calculate second verification digit
    sum_digits = sum(int(cpf[i]) * (11 - i) for i in range(10))
    expected_digit_2 = (sum_digits * 10 % 11) % 10
    if int(cpf[10]) != expected_digit_2:
        return False

    return True

def is_valid_cnpj(cnpj: str) -> bool:
    cnpj = re.sub(r'\D', '', cnpj)
    if len(cnpj) != 14:
        return False
    
    # Check for all same digits
    if cnpj == cnpj[0] * 14:
        return False

    # Calculate first verification digit
    weights_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum_digits = sum(int(cnpj[i]) * weights_1[i] for i in range(12))
    expected_digit_1 = 0 if sum_digits % 11 < 2 else 11 - (sum_digits % 11)
    if int(cnpj[12]) != expected_digit_1:
        return False

    # Calculate second verification digit
    weights_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum_digits = sum(int(cnpj[i]) * weights_2[i] for i in range(13))
    expected_digit_2 = 0 if sum_digits % 11 < 2 else 11 - (sum_digits % 11)
    if int(cnpj[13]) != expected_digit_2:
        return False

    return True

def is_valid_cpf_cnpj(document: str) -> bool:
    if not document:
        return False
        
    doc_clean = re.sub(r'\D', '', document)
    if len(doc_clean) == 11:
        return is_valid_cpf(doc_clean)
    elif len(doc_clean) == 14:
        return is_valid_cnpj(doc_clean)
    else:
        return False
