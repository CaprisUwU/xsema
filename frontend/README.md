# XSEMA Frontend

**Advanced NFT Security & Analytics Platform**

A modern, responsive React-based frontend for XSEMA, featuring comprehensive portfolio management, real-time market data, and advanced security analytics.

## 🚀 Features

### **Portfolio Management**
- **Advanced P&L Calculations**: Realized/unrealized gains with UK currency formatting (£)
- **Debt Tracking**: Monitor borrowing positions and liquidation risks
- **Tax Reporting**: Comprehensive tax calculations with UK date format (11/08/2025)
- **Risk Assessment**: Portfolio risk metrics and alerts

### **Market Data**
- **Real-time Floor Price Monitoring**: Live NFT collection floor prices
- **Market Cap Tracking**: Comprehensive asset market data
- **Cross-market Aggregation**: Multi-source data with arbitrage detection
- **Event Filtering & Subscriptions**: Customizable market alerts

### **Security & Analytics**
- **Security Scoring**: Portfolio security assessment
- **Wallet Clustering**: Advanced wallet analysis
- **Multi-chain Support**: Ethereum, Polygon, BSC, and more
- **Real-time Monitoring**: Continuous security surveillance

## 🎨 Design Features

- **UK Localization**: £ currency and UK date format (11/08/2025)
- **Dark/Light Mode**: Seamless theme switching
- **Responsive Design**: Mobile-first approach
- **Modern UI**: Beautiful gradients and animations
- **Accessibility**: WCAG compliant components

## 🛠️ Tech Stack

- **Frontend Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS + Custom Components
- **State Management**: Zustand + React Query
- **Routing**: React Router DOM
- **Animations**: Framer Motion
- **Charts**: Recharts
- **Icons**: Lucide React
- **Forms**: React Hook Form
- **Notifications**: React Hot Toast

## 📦 Installation

### Prerequisites
- Node.js 16+ 
- npm 8+ or yarn

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🔧 Configuration

### Environment Variables
Create a `.env.local` file in the frontend directory:

```env
VITE_API_BASE_URL=http://localhost:8001
VITE_APP_NAME=XSEMA
VITE_APP_VERSION=2.0.0
VITE_ENVIRONMENT=development
```

### UK Formatting
The application automatically uses UK formatting:

- **Currency**: £ symbol with proper formatting
- **Dates**: DD/MM/YYYY format (e.g., 11/08/2025)
- **Time**: 24-hour format (HH:mm)
- **Locale**: en-GB

## 📱 Component Structure

```
src/
├── components/
│   ├── dashboard/          # Dashboard components
│   ├── layout/            # Layout components
│   ├── portfolio/         # Portfolio management
│   ├── market/            # Market data components
│   └── security/          # Security components
├── pages/                 # Page components
├── hooks/                 # Custom React hooks
├── utils/                 # Utility functions
├── types/                 # TypeScript type definitions
├── context/               # React context providers
└── styles/                # Global styles
```

## 🎯 Key Components

### **StatCard**
Displays portfolio statistics with UK currency formatting:
```tsx
<StatCard
  title="Portfolio Value"
  value="£125,000.50"
  change={3250.75}
  changePercentage={2.67}
  trend="up"
/>
```

### **Dashboard**
Main dashboard with UK date formatting:
```tsx
// UK date format: Monday, 11 August 2025 at 14:30
const currentDate = format(new Date(), 'EEEE, d MMMM yyyy', { locale: enGB });
const currentTime = format(new Date(), 'HH:mm', { locale: enGB });
```

## 🌐 API Integration

The frontend integrates with the XSEMA backend API:

- **Base URL**: `http://localhost:8001` (development)
- **Authentication**: API key-based authentication
- **Real-time Updates**: WebSocket connections
- **Data Caching**: React Query for efficient data management

## 🚀 Deployment

### Development
```bash
npm run dev
# Server runs on http://localhost:5173
```

### Production Build
```bash
npm run build
# Output in dist/ directory
```

### Docker Deployment
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

## 📊 Performance

- **Bundle Size**: Optimized with Vite
- **Code Splitting**: Route-based code splitting
- **Lazy Loading**: Component lazy loading
- **Image Optimization**: WebP format support
- **Caching**: Efficient data caching strategies

## 🔒 Security Features

- **Input Validation**: Comprehensive form validation
- **XSS Protection**: Sanitized user inputs
- **CSRF Protection**: API request security
- **Secure Headers**: Security-focused HTTP headers

## 🧪 Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- **Documentation**: [docs.xsema.com](https://docs.xsema.com)
- **Issues**: GitHub Issues
- **Discord**: [discord.gg/xsema](https://discord.gg/xsema)

## 🔄 Updates

Stay updated with the latest features:
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **Releases**: GitHub Releases
- **Newsletter**: [newsletter.xsema.com](https://newsletter.xsema.com)

---

**Built with ❤️ by the XSEMA Team**

*Advanced NFT Security & Analytics Platform*
