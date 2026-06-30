"""
Role and data-access rules from ACCESS CONTROL AND PERFORMANCE.txt

Route access  — which app URLs each role may open
Data access   — what patient fields each role may see (for future patient views)
"""

# URL path prefix -> roles allowed (admin always included via user.has_role_access)
ROUTE_ACCESS = {
    '/reception/': ('reception',),
    '/triage/': ('triage',),
    '/doctor/': ('doctor',),
    '/pharmacy/': ('pharmacy',),
    '/lab/': ('lab',),
    '/nurse/': ('nurse',),
}

# Django app_name -> roles allowed (used by view decorator)
APP_ROLE_ACCESS = {
    'reception': ('reception',),
    'triage': ('triage',),
    'doctors': ('doctor',),
    'pharmacy': ('pharmacy',),
    'laboratory': ('lab',),
    'nurses': ('nurse',),
}

# Patient data visibility levels for future patient/visit models
DATA_ACCESS = {
    'admin': 'full',
    'reception': 'full',
    'doctor': 'no_payment',
    'triage': 'limited',
    'pharmacy': 'prescription_only',
    'lab': 'lab_limited',
    'nurse': 'nurse_limited',
}

DATA_ACCESS_FIELDS = {
    'full': {
        'name', 'age', 'gender', 'phone', 'address', 'visit_type', 'visit_number',
        'vitals', 'symptoms', 'diagnosis', 'prescription', 'payment_mode',
        'insurance', 'referral', 'lab_orders', 'day_of_stay', 'notes',
    },
    'no_payment': {
        'name', 'age', 'gender', 'phone', 'address', 'visit_type', 'visit_number',
        'vitals', 'symptoms', 'diagnosis', 'prescription', 'insurance', 'referral',
        'lab_orders', 'day_of_stay', 'notes',
    },
    'limited': {'name', 'age', 'visit_type', 'visit_number'},
    'prescription_only': {'name', 'prescription'},
    'lab_limited': {'name', 'age', 'lab_orders'},
    'nurse_limited': {'name', 'age', 'prescription', 'day_of_stay'},
}


def role_can_access_app(role, app_name):
    if role == 'admin':
        return True
    allowed = APP_ROLE_ACCESS.get(app_name, ())
    return role in allowed


def role_can_access_path(role, path):
    if role == 'admin':
        return True
    for prefix, roles in ROUTE_ACCESS.items():
        if path.startswith(prefix):
            return role in roles
    return True


def allowed_fields_for_role(role):
    level = DATA_ACCESS.get(role, 'limited')
    return DATA_ACCESS_FIELDS.get(level, set())


def filter_patient_fields(role, data):
    """Return a copy of patient data dict with only fields this role may see."""
    if role == 'admin':
        return dict(data)
    allowed = allowed_fields_for_role(role)
    return {key: value for key, value in data.items() if key in allowed}
