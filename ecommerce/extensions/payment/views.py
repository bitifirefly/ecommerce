""" Views for interacting with the payment processor. """
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.generic import View
from oscar.apps.checkout.mixins import OrderPlacementMixin
from oscar.apps.payment.models import SourceType

from ecommerce.extensions.order.models import Order
from ecommerce.extensions.fulfillment.status import ORDER
from ecommerce.extensions.fulfillment.mixins import FulfillmentMixin
from ecommerce.extensions.payment.constants import ProcessorConstants as PC
from ecommerce.extensions.payment.helpers import get_processor_class


class ProcessorsListView(View):
    """
    Provides information about payment processors.
    """
    _names = None

    def get(self, request):
        """
        Get the names of configured payment processors.

        Returns:
            list of unicode
        """
        if ProcessorsListView._names is None:
            # processor settings do not change at runtime, so memoize this list once for all responses.
            ProcessorsListView._names = [get_processor_class(path).NAME for path in settings.PAYMENT_PROCESSORS]
        return JsonResponse(ProcessorsListView._names, safe=False)


class CybersourceResponseView(View, OrderPlacementMixin, FulfillmentMixin):
    """
    Accept response from the processor and fulfill the request
    """

    def post(self, request):
        """ Handle the response we've been given from the processor. """
        payment_processor = get_processor_class(settings.PAYMENT_PROCESSORS[0])
        # check the data we get
        params = request.POST.dict()
        result = payment_processor().handle_processor_response(params)
        if result[PC.SUCCESS]:
            # get the order
            order = Order.objects.get(number=result[PC.ORDER_NUMBER])
            # register the money in Oscar
            self._register_payment(order, payment_processor.NAME)
            # fulfill the order
            self._fulfill_order(order)

        # It doesn't matter how we respond to the payment processor if the
        # payment failed.
        return HttpResponse()

    def _register_payment(self, order, processor_name):
        """
        Records the payment source and event and updates the order status

        Args:
            order (Order): the order that is being paid for
            processor_name (str): the name of the processor that will be processing this payment
        Returns:
            None
        """

        # get the source
        source_type, _ = SourceType.objects.get_or_create(name=processor_name)
        source = source_type.sources.model(
            source_type=source_type, amount_allocated=order.total_excl_tax, currency=order.currency
        )

        # record payment events
        self.add_payment_source(source)
        self.add_payment_event(PC.PAID_EVENT_NAME, order.total_excl_tax, order.number)
        self.save_payment_details(order)

        # update the status of the order
        order.set_status(ORDER.PAID)
