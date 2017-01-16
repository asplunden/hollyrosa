from tw2.forms import SingleSelectField

class SingleSelectFieldMod(SingleSelectField):
    def prepare(self):
        """
        Neat trick: let value be a pair (value, options) and unpack accordingly
        """
        if not self.value:
            self.value = ''
        if isinstance(self.value, (list, tuple)):
            #self.value = self.value[0]
            #self.options = ['x1','z1']
            (self.value, self.options) = self.value
        
        #if not hasattr(self, '_validated') and self.item_validator:
        #    self.value = [
        #        self.item_validator.from_python(v) for v in self.value
        #    ]
        super(SingleSelectField, self).prepare()
        print self.options