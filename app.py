from tracemalloc import start
from flask import Flask, jsonify,request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import ForeignKey


app =Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventoryManagement.db'
db = SQLAlchemy(app)
app.debug=True

class Product(db.Model): #create a class fro Product model
    __tablename__ = 'products'
    #defining column for thr Product model
    Product_id = db.Column(db.String(200),primary_key=True)
    Name = db.Column(db.String(200),nullable=False,unique=True)
    Price = db.Column(db.Integer,nullable=False)
    Quantity = db.Column(db.Integer,nullable=False)

    #creating relationship with the Sale tabel
    sales = db.relationship("Sale", back_populates="products")

    def __repr__(self):
      return '<Product %r>' % self.Product_id

class Sale(db.Model):  #create a class for Sale model
    __tablename__= 'sale'
    #Defining column for the Sale model
    Sale_id=db.Column(db.String(200),primary_key=True) 

    #Create a column with referencing to product id
    Product_id= db.Column(db.String(200),ForeignKey("products.Product_id"))

    #create relationship with the Product table
    products = db.relationship("Product", back_populates="sales")

    Quantity_sold=db.Column(db.Integer)
    Date_of_sale= db.Column(db.Date)

    def __repr__(self):  #how the model will be shown
      return '<Sale %r>' % self.Sale_id


with app.app_context(): #create the table
    db.create_all()

@app.route('/AddProduct/', methods=["POST"]) # route to add product into the product table
def productAdd():
    if(request.method=="POST" and len(request.values)==4):

        id=request.values.get('Product_id')
        name=request.values.get('Name')
        Price=request.values.get('Price')
        Quantity=request.values.get('Quantity')

        exist=Product.query.filter_by(Product_id=id).all()
        
        if(len(exist)==0):
            new_product=Product(
                Product_id=id,
                Name=name,
                Price=Price,
                Quantity=Quantity
            )

            try:
                db.session.add(new_product)
                db.session.commit()
                return "Product Added"
            except:
                return "There Was an issue while add a new Product, please choose unique Product name"
        else:
            return" Please enter a unique id"
    else:
        return "Please Input all the require Fill and use POST method"


@app.route('/updateProduct/<id>',methods=['POST']) #route to update the product in the Product table
def productUpdate(id):
    product = Product.query.get_or_404(id)  #Get the product using the id in the url

    if request.method == "POST":
        product.Price = request.values.get('Price') #updating the old price with the new one
        product.Quantity = request.values.get('Quantity') #updating the old quantity with the new one

        db.session.commit()

        product=Product.query.get_or_404(id)
        return ({"Price" :product.Price,"Quantity":product.Quantity})
    
    else:
        return "Please use POST method"


@app.route('/updateSale/',methods=['POST']) #create route to update the sale
def saleUpdate():
    if(request.method=='POST') and ('Sale_id' in request.values):
        
        id=request.values.get('Sale_id')
        Prod_id=request.values.get('Product_id')
        Date=request.values.get('Date_of_sale')
        Quantity=request.values.get('Quantity_sold')

        Date=datetime.strptime(Date,'%d/%m/%Y').date()  # Create datetime format of the date enter in the postman

        # print(date.today().strftime("%Y-%m-%d"))
        
        new_sale=Sale(
            Sale_id=id,
            Product_id=Prod_id,
            Date_of_sale=Date,
            Quantity_sold=Quantity
        )

        product = Product.query.get_or_404(Prod_id)  # getting the table product

        if(product.Quantity>=int(Quantity)):  #checking if the quantity sold is less than the available quantity
    
            try:
                product.Quantity=product.Quantity-int(Quantity)  # updating the product table quantity after the product is sold
                db.session.add(new_sale)
                db.session.commit()
                return "Item sold"

            except:
                return "There is problem with update sales"
        
        else:
            return "The Quantity is more than in the Inventory"

    else:
        return " Use POST method"


@app.route('/report/',methods=['GET']) # create route to generate report
def generateReport():
    startdate=request.args.get('start')
    enddate=request.args.get('end')

    print(startdate)

    Data=Sale.query.where(Sale.Date_of_sale.between(startdate,enddate)).all()#storing the item they are between the date range

    print(Data)

    if(len(Data)>0): # checking if the data is present or not
        
        Result=[] 
        Total_Revenue=0

        for i in Data:
            item={}
            item['SaleID']=i.Sale_id
            item['ProductID']=i.Product_id
            item['Quantity']=i.Quantity_sold
            item['Date_of_Sale']=i.Date_of_sale
            product=Product.query.get_or_404(i.Product_id)  # Getting the product table
            item['Total Amount']=product.Price*i.Quantity_sold  # calculate the total amount for each sale
            Total_Revenue+=item['Total Amount']          #Calculating the Total revenue

            Result.append(item)
        
        Result.append({"Total Revenue":Total_Revenue})
        return jsonify(Result)  #converting into String to return it back to the browser
    else:
        return "No Data"

@app.route('/')
def check():
    return "The Inventory Management is working"   #when the app is start

if __name__ == '__main__': # run the app
    app.run()