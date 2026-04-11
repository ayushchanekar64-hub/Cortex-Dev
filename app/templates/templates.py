"""
Predefined templates for Cortex-Dev
"""
from typing import Dict, List, Any


# Template definitions
TEMPLATES = {
    "ecommerce": {
        "id": "ecommerce",
        "name": "E-commerce App",
        "description": "Full-featured online store with product catalog, shopping cart, and checkout",
        "icon": "🛒",
        "features": [
            "Product catalog with categories",
            "Shopping cart functionality",
            "User authentication",
            "Checkout process",
            "Order management"
        ],
        "frontend_files": {
            "frontend/src/App.tsx": """import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import ProductList from './components/ProductList'
import Cart from './components/Cart'
import Checkout from './components/Checkout'
import './styles/globals.css'

function App() {
  const [cart, setCart] = useState([])
  
  const addToCart = (product) => {
    setCart([...cart, product])
  }
  
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Header cartCount={cart.length} />
        <Routes>
          <Route path="/" element={<ProductList addToCart={addToCart} />} />
          <Route path="/cart" element={<Cart cart={cart} setCart={setCart} />} />
          <Route path="/checkout" element={<Checkout cart={cart} />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App""",
            "frontend/src/components/Header.tsx": """import React from 'react'
import { Link } from 'react-router-dom'

function Header({ cartCount }) {
  return (
    <header className="bg-white shadow-md">
      <nav className="container mx-auto px-4 py-4 flex justify-between items-center">
        <Link to="/" className="text-2xl font-bold text-indigo-600">
          ShopHub
        </Link>
        <div className="flex space-x-6">
          <Link to="/" className="text-gray-700 hover:text-indigo-600">Products</Link>
          <Link to="/cart" className="text-gray-700 hover:text-indigo-600">
            Cart ({cartCount})
          </Link>
        </div>
      </nav>
    </header>
  )
}

export default Header""",
            "frontend/src/components/ProductList.tsx": """import React, { useState } from 'react'

const products = [
  { id: 1, name: "Laptop", price: 999, image: "https://via.placeholder.com/200" },
  { id: 2, name: "Phone", price: 699, image: "https://via.placeholder.com/200" },
  { id: 3, name: "Headphones", price: 199, image: "https://via.placeholder.com/200" },
]

function ProductList({ addToCart }) {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Products</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {products.map(product => (
          <div key={product.id} className="bg-white rounded-lg shadow-md p-4">
            <img src={product.image} alt={product.name} className="w-full h-48 object-cover mb-4" />
            <h3 className="text-xl font-semibold mb-2">{product.name}</h3>
            <p className="text-gray-600 mb-4">${product.price}</p>
            <button 
              onClick={() => addToCart(product)}
              className="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700"
            >
              Add to Cart
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}

export default ProductList""",
            "frontend/src/components/Cart.tsx": """import React from 'react'

function Cart({ cart, setCart }) {
  const total = cart.reduce((sum, item) => sum + item.price, 0)
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Shopping Cart</h1>
      {cart.length === 0 ? (
        <p className="text-gray-600">Your cart is empty</p>
      ) : (
        <div>
          {cart.map((item, index) => (
            <div key={index} className="bg-white rounded-lg shadow-md p-4 mb-4 flex justify-between items-center">
              <div>
                <h3 className="text-xl font-semibold">{item.name}</h3>
                <p className="text-gray-600">${item.price}</p>
              </div>
              <button 
                onClick={() => setCart(cart.filter((_, i) => i !== index))}
                className="text-red-600 hover:text-red-700"
              >
                Remove
              </button>
            </div>
          ))}
          <div className="bg-white rounded-lg shadow-md p-4 mt-4">
            <p className="text-2xl font-bold">Total: ${total}</p>
          </div>
        </div>
      )}
    </div>
  )
}

export default Cart""",
            "frontend/src/components/Checkout.tsx": """import React from 'react'

function Checkout({ cart }) {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Checkout</h1>
      <div className="bg-white rounded-lg shadow-md p-6">
        <form className="space-y-4">
          <div>
            <label className="block text-gray-700 mb-2">Full Name</label>
            <input type="text" className="w-full border rounded-lg px-4 py-2" />
          </div>
          <div>
            <label className="block text-gray-700 mb-2">Email</label>
            <input type="email" className="w-full border rounded-lg px-4 py-2" />
          </div>
          <div>
            <label className="block text-gray-700 mb-2">Address</label>
            <textarea className="w-full border rounded-lg px-4 py-2" rows="3"></textarea>
          </div>
          <button type="submit" className="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700">
            Place Order
          </button>
        </form>
      </div>
    </div>
  )
}

export default Checkout""",
            "frontend/src/styles/globals.css": """* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', sans-serif;
  line-height: 1.6;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}""",
            "frontend/package.json": """{
  "name": "ecommerce-app",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.0.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build"
  }
}"""
        },
        "backend_files": {
            "backend/main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import products, cart, orders

app = FastAPI(title="E-commerce API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router, prefix="/api")
app.include_router(cart.router, prefix="/api")
app.include_router(orders.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "E-commerce API"}""",
            "backend/app/models.py": """from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)
    description = Column(String)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    customer_name = Column(String)
    customer_email = Column(String)
    total = Column(Float)""",
            "backend/app/routes/products.py": """from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class Product(BaseModel):
    id: int
    name: str
    price: float
    description: str

products_db = [
    Product(id=1, name="Laptop", price=999.99, description="High-performance laptop"),
    Product(id=2, name="Phone", price=699.99, description="Smartphone"),
]

@router.get("/products")
def get_products():
    return products_db

@router.get("/products/{product_id}")
def get_product(product_id: int):
    for product in products_db:
        if product.id == product_id:
            return product
    return {"error": "Product not found"}""",
            "backend/app/routes/cart.py": """from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class CartItem(BaseModel):
    product_id: int
    quantity: int

cart_db = []

@router.post("/cart/add")
def add_to_cart(item: CartItem):
    cart_db.append(item)
    return {"message": "Added to cart"}

@router.get("/cart")
def get_cart():
    return cart_db""",
            "backend/app/routes/orders.py": """from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class Order(BaseModel):
    customer_name: str
    customer_email: str
    total: float

@router.post("/orders")
def create_order(order: Order):
    return {"message": "Order created", "order_id": 123}""",
            "backend/requirements.txt": """fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0"""
        }
    },
    "auth": {
        "id": "auth",
        "name": "Auth System",
        "description": "Complete authentication system with login, registration, and user management",
        "icon": "🔐",
        "features": [
            "User registration",
            "Login/logout",
            "Password reset",
            "Session management",
            "Role-based access"
        ],
        "frontend_files": {
            "frontend/src/App.tsx": """import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Login from './components/Login'
import Register from './components/Register'
import Dashboard from './components/Dashboard'
import './styles/globals.css'

function App() {
  const [user, setUser] = useState(null)
  
  useEffect(() => {
    const savedUser = localStorage.getItem('user')
    if (savedUser) setUser(JSON.parse(savedUser))
  }, [])
  
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login setUser={setUser} />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={user ? <Dashboard user={user} /> : <Navigate to="/login" />} />
        <Route path="/" element={user ? <Navigate to="/dashboard" /> : <Navigate to="/login" />} />
      </Routes>
    </Router>
  )
}

export default App""",
            "frontend/src/components/Login.tsx": """import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

function Login({ setUser }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const navigate = useNavigate()
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    // Simulate login
    const user = { email, name: email.split('@')[0] }
    setUser(user)
    localStorage.setItem('user', JSON.stringify(user))
    navigate('/dashboard')
  }
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-96">
        <h2 className="text-2xl font-bold mb-6">Login</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full border rounded-lg px-4 py-2"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full border rounded-lg px-4 py-2"
          />
          <button type="submit" className="w-full bg-indigo-600 text-white py-2 rounded-lg">
            Login
          </button>
        </form>
      </div>
    </div>
  )
}

export default Login""",
            "frontend/src/components/Register.tsx": """import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

function Register() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const navigate = useNavigate()
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    // Simulate registration
    navigate('/login')
  }
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-96">
        <h2 className="text-2xl font-bold mb-6">Register</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full border rounded-lg px-4 py-2"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full border rounded-lg px-4 py-2"
          />
          <button type="submit" className="w-full bg-indigo-600 text-white py-2 rounded-lg">
            Register
          </button>
        </form>
      </div>
    </div>
  )
}

export default Register""",
            "frontend/src/components/Dashboard.tsx": """import React from 'react'
import { useNavigate } from 'react-router-dom'

function Dashboard({ user }) {
  const navigate = useNavigate()
  
  const handleLogout = () => {
    localStorage.removeItem('user')
    navigate('/login')
  }
  
  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-md p-4">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-xl font-bold">Dashboard</h1>
          <button onClick={handleLogout} className="text-red-600">Logout</button>
        </div>
      </nav>
      <div className="container mx-auto p-8">
        <h2 className="text-2xl font-bold mb-4">Welcome, {user.name}!</h2>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <p className="text-gray-600">Email: {user.email}</p>
        </div>
      </div>
    </div>
  )
}

export default Dashboard""",
            "frontend/src/styles/globals.css": """* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', sans-serif;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}""",
            "frontend/package.json": """{
  "name": "auth-system",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.0.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build"
  }
}"""
        },
        "backend_files": {
            "backend/main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, users

app = FastAPI(title="Auth API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Auth API"}""",
            "backend/app/models.py": """from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)
    name = Column(String)""",
            "backend/app/routes/auth.py": """from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import hashlib

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str

users_db = []

@router.post("/auth/register")
def register(request: RegisterRequest):
    for user in users_db:
        if user.email == request.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = hashlib.sha256(request.password.encode()).hexdigest()
    user = {"email": request.email, "password": hashed_password, "name": request.name}
    users_db.append(user)
    return {"message": "User registered"}

@router.post("/auth/login")
def login(request: LoginRequest):
    hashed_password = hashlib.sha256(request.password.encode()).hexdigest()
    for user in users_db:
        if user.email == request.email and user.password == hashed_password:
            return {"message": "Login successful", "user": {"email": user.email, "name": user.name}}
    raise HTTPException(status_code=401, detail="Invalid credentials")""",
            "backend/app/routes/users.py": """from fastapi import APIRouter

router = APIRouter()

@router.get("/users/me")
def get_current_user():
    return {"user": "current_user"}""",
            "backend/requirements.txt": """fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0"""
        }
    },
    "dashboard": {
        "id": "dashboard",
        "name": "Dashboard App",
        "description": "Analytics dashboard with charts, metrics, and data visualization",
        "icon": "📊",
        "features": [
            "Data visualization charts",
            "Key metrics display",
            "Real-time updates",
            "Filter and search",
            "Export functionality"
        ],
        "frontend_files": {
            "frontend/src/App.tsx": """import React from 'react'
import Sidebar from './components/Sidebar'
import Dashboard from './components/Dashboard'
import './styles/globals.css'

function App() {
  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar />
      <Dashboard />
    </div>
  )
}

export default App""",
            "frontend/src/components/Sidebar.tsx": """import React from 'react'

function Sidebar() {
  return (
    <div className="w-64 bg-gray-800 text-white">
      <div className="p-4">
        <h1 className="text-2xl font-bold">Dashboard</h1>
      </div>
      <nav className="mt-4">
        <a href="#" className="block px-4 py-2 hover:bg-gray-700">Overview</a>
        <a href="#" className="block px-4 py-2 hover:bg-gray-700">Analytics</a>
        <a href="#" className="block px-4 py-2 hover:bg-gray-700">Reports</a>
        <a href="#" className="block px-4 py-2 hover:bg-gray-700">Settings</a>
      </nav>
    </div>
  )
}

export default Sidebar""",
            "frontend/src/components/Dashboard.tsx": """import React from 'react'

function Dashboard() {
  const metrics = [
    { label: "Total Users", value: "1,234", change: "+12%" },
    { label: "Revenue", value: "$45,678", change: "+8%" },
    { label: "Orders", value: "567", change: "+23%" },
    { label: "Conversion", value: "3.2%", change: "-2%" },
  ]
  
  return (
    <div className="flex-1 p-8">
      <h1 className="text-3xl font-bold mb-8">Overview</h1>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        {metrics.map((metric, index) => (
          <div key={index} className="bg-white p-6 rounded-lg shadow-md">
            <p className="text-gray-600">{metric.label}</p>
            <p className="text-2xl font-bold">{metric.value}</p>
            <p className={`text-sm ${metric.change.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
              {metric.change}
            </p>
          </div>
        ))}
      </div>
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-bold mb-4">Recent Activity</h2>
        <div className="space-y-2">
          <div className="p-3 bg-gray-50 rounded">User signed up</div>
          <div className="p-3 bg-gray-50 rounded">New order placed</div>
          <div className="p-3 bg-gray-50 rounded">Product updated</div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard""",
            "frontend/src/styles/globals.css": """* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', sans-serif;
}""",
            "frontend/package.json": """{
  "name": "dashboard-app",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build"
  }
}"""
        },
        "backend_files": {
            "backend/main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import analytics, metrics

app = FastAPI(title="Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analytics.router, prefix="/api")
app.include_router(metrics.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Dashboard API"}""",
            "backend/app/models.py": """from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Metric(Base):
    __tablename__ = "metrics"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    value = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)""",
            "backend/app/routes/analytics.py": """from fastapi import APIRouter

router = APIRouter()

@router.get("/analytics/data")
def get_analytics_data():
    return {
        "users": 1234,
        "revenue": 45678,
        "orders": 567,
        "conversion": 3.2
    }""",
            "backend/app/routes/metrics.py": """from fastapi import APIRouter

router = APIRouter()

@router.get("/metrics/summary")
def get_metrics_summary():
    return {
        "total_users": 1234,
        "active_users": 856,
        "new_users": 234
    }""",
            "backend/requirements.txt": """fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0"""
        }
    }
}


def get_template(template_id: str) -> Dict[str, Any]:
    """Get a template by ID"""
    return TEMPLATES.get(template_id)


def get_all_templates() -> List[Dict[str, Any]]:
    """Get all available templates"""
    return list(TEMPLATES.values())


def merge_template_with_generation(template: Dict[str, Any], generated_files: Dict[str, str], prompt: str) -> Dict[str, str]:
    """Merge template files with AI-generated files based on prompt"""
    merged_files = {}
    
    # Start with template files
    if "frontend_files" in template:
        merged_files.update(template["frontend_files"])
    if "backend_files" in template:
        merged_files.update(template["backend_files"])
    
    # Override with AI-generated files for customization
    if generated_files:
        merged_files.update(generated_files)
    
    return merged_files
