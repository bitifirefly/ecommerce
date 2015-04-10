"""Ecommerce API constants."""


class APIDictionaryKeys(object):
    """Dictionary keys used repeatedly in the ecommerce API."""
    ORDER_NUMBER = u'number'
    SHIPPING_METHOD = u'shipping_method'
    SHIPPING_CHARGE = u'shipping_charge'
    ORDER_TOTAL = u'total'


class APIConstants(object):
    """Constants used throughout the ecommerce API."""
    KEYS = APIDictionaryKeys()
