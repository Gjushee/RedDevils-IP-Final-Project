from django import forms


class CheckoutForm(forms.Form):
    # Contact
    full_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'John Smith'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control', 'placeholder': 'john@example.com'}))
    phone = forms.CharField(required=False, max_length=20, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': '+44 7700 000000'}))

    # Billing address
    address_line1 = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': '123 Main Street'}))
    address_line2 = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Apartment, suite, etc.'}))
    city = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Manchester'}))
    postcode = forms.CharField(max_length=20, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'M1 1AE'}))
    country = forms.CharField(max_length=100, initial='United Kingdom', widget=forms.TextInput(attrs={
        'class': 'form-control'}))

    # Card details
    card_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Name on card',
        'autocomplete': 'cc-name'}))
    card_number = forms.CharField(max_length=19, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': '1234 5678 9012 3456',
        'autocomplete': 'cc-number', 'inputmode': 'numeric'}))
    expiry = forms.CharField(max_length=5, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'MM/YY',
        'autocomplete': 'cc-exp', 'inputmode': 'numeric'}))
    cvv = forms.CharField(max_length=4, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': '•••',
        'autocomplete': 'cc-csc', 'inputmode': 'numeric',
        'id': 'id_cvv'}))

    def clean_card_number(self):
        number = self.cleaned_data['card_number'].replace(' ', '')
        if not number.isdigit() or len(number) not in (15, 16):
            raise forms.ValidationError('Enter a valid 15 or 16 digit card number.')
        return number

    def clean_expiry(self):
        expiry = self.cleaned_data['expiry']
        if '/' not in expiry:
            raise forms.ValidationError('Enter expiry as MM/YY.')
        month, year = expiry.split('/', 1)
        if not month.isdigit() or not year.isdigit() or not (1 <= int(month) <= 12):
            raise forms.ValidationError('Enter a valid expiry date.')
        return expiry

    def clean_cvv(self):
        cvv = self.cleaned_data['cvv']
        if not cvv.isdigit() or len(cvv) not in (3, 4):
            raise forms.ValidationError('Enter a valid 3 or 4 digit CVV.')
        return cvv
