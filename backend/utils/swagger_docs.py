"""
Swagger/OpenAPI Documentation for Smart Locomotive Health Monitor API
Generated using Flasgger with Flask integration
"""

from flasgger import Swagger, swag_from

def init_swagger(app):
    """Initialize Swagger documentation"""
    swagger = Swagger(
        app,
        template={
            'swagger': '3.0.0',
            'info': {
                'title': 'Smart Locomotive Health Monitor API',
                'version': '2.0.0',
                'description': 'AI-powered predictive maintenance system for Bangladesh Railways',
                'contact': {
                    'name': 'Development Team',
                    'email': 'support@railway.gov.bd'
                }
            },
            'host': 'localhost:5000',
            'basePath': '/api',
            'schemes': ['http', 'https'],
            'securityDefinitions': {
                'Bearer': {
                    'type': 'apiKey',
                    'name': 'Authorization',
                    'in': 'header',
                    'description': 'JWT token (Bearer <token>)'
                }
            }
        },
        config={
            'headers': [],
            'specs': [
                {
                    'endpoint': 'apispec',
                    'route': '/apispec.json',
                    'rule_filter': lambda rule: True,
                    'model_filter': lambda tag: True,
                }
            ],
            'static_url_path': '/flasgger_static',
            'swagger_ui': True,
            'specs_route': '/docs'
        }
    )
    return swagger


# API Documentation Specs

AUTH_REGISTER_SPEC = {
    'tags': ['Authentication'],
    'summary': 'Register a new user',
    'description': 'Create a new user account',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'example': 'john_doe'},
                    'email': {'type': 'string', 'example': 'john@example.com'},
                    'password': {'type': 'string', 'example': 'secure_password'},
                    'full_name': {'type': 'string', 'example': 'John Doe'},
                    'department': {'type': 'string', 'example': 'Maintenance'}
                },
                'required': ['username', 'email', 'password']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'User registered successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'example': 'success'},
                    'token': {'type': 'string'},
                    'user': {'type': 'object'}
                }
            }
        },
        400: {'description': 'Missing required fields'},
        409: {'description': 'User already exists'}
    }
}

AUTH_LOGIN_SPEC = {
    'tags': ['Authentication'],
    'summary': 'User login',
    'description': 'Authenticate user and get JWT token',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'password': {'type': 'string'}
                },
                'required': ['username', 'password']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Login successful',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'token': {'type': 'string'},
                    'user': {'type': 'object'}
                }
            }
        },
        401: {'description': 'Invalid credentials'}
    }
}

LOCOMOTIVES_LIST_SPEC = {
    'tags': ['Locomotives'],
    'summary': 'List all locomotives',
    'description': 'Get paginated list of all locomotives',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'page',
            'in': 'query',
            'type': 'integer',
            'default': 1,
            'description': 'Page number'
        },
        {
            'name': 'per_page',
            'in': 'query',
            'type': 'integer',
            'default': 20,
            'description': 'Results per page'
        },
        {
            'name': 'status',
            'in': 'query',
            'type': 'string',
            'description': 'Filter by status (ACTIVE, INACTIVE, MAINTENANCE)'
        }
    ],
    'responses': {
        200: {
            'description': 'List of locomotives',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'count': {'type': 'integer'},
                    'locomotives': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'string'},
                                'name': {'type': 'string'},
                                'status': {'type': 'string'},
                                'health_score': {'type': 'number'},
                                'current_risk': {'type': 'number'}
                            }
                        }
                    }
                }
            }
        },
        401: {'description': 'Unauthorized'}
    }
}

LOCOMOTIVE_DETAIL_SPEC = {
    'tags': ['Locomotives'],
    'summary': 'Get locomotive details',
    'description': 'Get detailed information about a specific locomotive',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'loco_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'Locomotive ID'
        }
    ],
    'responses': {
        200: {
            'description': 'Locomotive details',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'locomotive': {'type': 'object'}
                }
            }
        },
        404: {'description': 'Locomotive not found'}
    }
}

HEALTH_ANALYSIS_SPEC = {
    'tags': ['Health Analysis'],
    'summary': 'Perform health analysis',
    'description': 'Analyze locomotive health based on sensor data',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'loco_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'Locomotive ID'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'temperature': {'type': 'number', 'example': 85.5},
                    'vibration': {'type': 'number', 'example': 5.2},
                    'pressure': {'type': 'number', 'example': 150},
                    'oil_quality': {'type': 'number', 'example': 25},
                    'mileage': {'type': 'number', 'example': 150000},
                    'latitude': {'type': 'number', 'example': 23.7275},
                    'longitude': {'type': 'number', 'example': 90.4086}
                },
                'required': ['temperature', 'vibration', 'pressure', 'oil_quality', 'mileage']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Health analysis results',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'analysis': {
                        'type': 'object',
                        'properties': {
                            'risk_score': {'type': 'number'},
                            'health_score': {'type': 'number'},
                            'risk_category': {'type': 'string'},
                            'component_risks': {'type': 'object'},
                            'recommendations': {'type': 'array'}
                        }
                    }
                }
            }
        },
        404: {'description': 'Locomotive not found'}
    }
}

ALERTS_LIST_SPEC = {
    'tags': ['Alerts'],
    'summary': 'Get locomotive alerts',
    'description': 'Retrieve all alerts for a specific locomotive',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'loco_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'Locomotive ID'
        },
        {
            'name': 'include_resolved',
            'in': 'query',
            'type': 'boolean',
            'default': False,
            'description': 'Include resolved alerts'
        },
        {
            'name': 'severity',
            'in': 'query',
            'type': 'string',
            'description': 'Filter by severity (CRITICAL, WARNING, INFO)'
        }
    ],
    'responses': {
        200: {
            'description': 'List of alerts',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'count': {'type': 'integer'},
                    'alerts': {'type': 'array'}
                }
            }
        },
        404: {'description': 'Locomotive not found'}
    }
}

PREDICTIONS_LIST_SPEC = {
    'tags': ['Predictions'],
    'summary': 'Get failure predictions',
    'description': 'Retrieve failure predictions for locomotive components',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'loco_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'Locomotive ID'
        }
    ],
    'responses': {
        200: {
            'description': 'List of predictions',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'count': {'type': 'integer'},
                    'predictions': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'component': {'type': 'string'},
                                'failure_probability': {'type': 'number'},
                                'hours_to_failure': {'type': 'number'},
                                'confidence_score': {'type': 'number'}
                            }
                        }
                    }
                }
            }
        },
        404: {'description': 'Locomotive not found'}
    }
}

MAINTENANCE_SCHEDULE_SPEC = {
    'tags': ['Maintenance'],
    'summary': 'Get maintenance schedule',
    'description': 'Retrieve maintenance schedule for a locomotive',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'loco_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'Locomotive ID'
        },
        {
            'name': 'status',
            'in': 'query',
            'type': 'string',
            'description': 'Filter by status (SCHEDULED, IN_PROGRESS, COMPLETED)'
        }
    ],
    'responses': {
        200: {
            'description': 'Maintenance schedules',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'count': {'type': 'integer'},
                    'schedules': {'type': 'array'}
                }
            }
        },
        404: {'description': 'Locomotive not found'}
    }
}

DASHBOARD_SUMMARY_SPEC = {
    'tags': ['Dashboard'],
    'summary': 'Get dashboard summary',
    'description': 'Get fleet-wide statistics for the dashboard',
    'security': [{'Bearer': []}],
    'responses': {
        200: {
            'description': 'Dashboard summary data',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'summary': {
                        'type': 'object',
                        'properties': {
                            'total_locomotives': {'type': 'integer'},
                            'active_locomotives': {'type': 'integer'},
                            'critical_alerts': {'type': 'integer'},
                            'average_health': {'type': 'number'},
                            'maintenance_due': {'type': 'integer'}
                        }
                    }
                }
            }
        },
        401: {'description': 'Unauthorized'}
    }
}
