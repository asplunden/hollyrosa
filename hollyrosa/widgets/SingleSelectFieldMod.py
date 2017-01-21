from tw2.forms import SingleSelectField
import tw2.core as twc

class SingleSelectFieldMod(SingleSelectField):
    def prepare(self):
        """
        Trick that ultimately wont work well: let value be a pair (value, options) and unpack accordingly.
        The problem is that if the form the widget is used in has a validation error, 
        the widget will NOT get the tupple from the WSGI saved state but only the value, so the option list will be lost.
        
        In short, dont use this widget.
        """
        if not self.value:
            self.value = ''
        if isinstance(self.value, (list, tuple)):
            (self.value, self.options) = self.value
        
        super(SingleSelectFieldMod, self).prepare()