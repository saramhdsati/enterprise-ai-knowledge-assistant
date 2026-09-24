def get_department(filename):
    prefix = filename.split('_')[0]
    mapping = {
        "hr": "HR",
        "it": "IT",
        "company": "Company"
    }
    return mapping.get(prefix, "General")