from razorpay import Client
from rest_framework.exceptions import ValidationError
from rest_framework import status

class RazorpayClient:  
    def verify_payment_signature(self, razorpay_order_id, razorpay_payment_id, razorpay_signature):
        try:
            client = Client(auth=(
                'rzp_test_TpsHVKhrkZuIUJ',
                'OJzAGp6Vqx8yu2qgeHhz4y3o'
            ))

            self.verify_signature = client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })

            return self.verify_signature

        except Exception as e:
            raise ValidationError(
                {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": str(e)
                }
            )