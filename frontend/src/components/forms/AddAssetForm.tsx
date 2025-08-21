import React, { useState } from 'react';
import { X, Plus, Wallet, Calendar, PoundSterling } from 'lucide-react';

interface AddAssetFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (asset: AssetData) => void;
}

interface AssetData {
  name: string;
  symbol: string;
  contractAddress: string;
  chain: string;
  purchasePrice: number;
  purchaseDate: string;
  quantity: number;
  notes: string;
}

const AddAssetForm: React.FC<AddAssetFormProps> = ({ isOpen, onClose, onSubmit }) => {
  const [formData, setFormData] = useState<AssetData>({
    name: '',
    symbol: '',
    contractAddress: '',
    chain: 'Ethereum',
    purchasePrice: 0,
    purchaseDate: new Date().toISOString().split('T')[0],
    quantity: 1,
    notes: ''
  });

  const [errors, setErrors] = useState<Partial<AssetData>>({});

  const chains = ['Ethereum', 'Polygon', 'BSC', 'Arbitrum', 'Optimism', 'Base', 'Avalanche', 'Fantom', 'Solana'];

  const validateForm = (): boolean => {
    const newErrors: Partial<AssetData> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Asset name is required';
    }
    if (!formData.symbol.trim()) {
      newErrors.symbol = 'Symbol is required';
    }
    if (!formData.contractAddress.trim()) {
      newErrors.contractAddress = 'Contract address is required';
    }
    if (formData.purchasePrice <= 0) {
      newErrors.purchasePrice = 'Purchase price must be greater than 0';
    }
    if (formData.quantity <= 0) {
      newErrors.quantity = 'Quantity must be greater than 0';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit(formData);
      onClose();
      setFormData({
        name: '',
        symbol: '',
        contractAddress: '',
        chain: 'Ethereum',
        purchasePrice: 0,
        purchaseDate: new Date().toISOString().split('T')[0],
        quantity: 1,
        notes: ''
      });
    }
  };

  const handleInputChange = (field: keyof AssetData, value: string | number) => {
    if (field === 'purchasePrice' || field === 'quantity') {
      const numValue = typeof value === 'string' ? parseFloat(value) || 0 : value;
      setFormData(prev => ({ ...prev, [field]: numValue as any }));
    } else {
      const strValue = typeof value === 'string' ? value : String(value);
      setFormData(prev => ({ ...prev, [field]: strValue as any }));
    }
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-slate-800 rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-700">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
              <Plus className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-slate-900 dark:text-white">
                Add New Asset
              </h2>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Add a new NFT to your portfolio
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
            aria-label="Close form"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Asset Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-slate-900 dark:text-white flex items-center">
              <Wallet className="w-5 h-5 mr-2 text-blue-600" />
              Asset Information
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Asset Name *
                </label>
                <input
                  type="text"
                  id="name"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.name 
                      ? 'border-red-300 dark:border-red-600 bg-red-50 dark:bg-red-900/20' 
                      : 'border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700'
                  } text-slate-900 dark:text-white`}
                  placeholder="e.g., Bored Ape Yacht Club #1234"
                />
                {errors.name && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.name}</p>
                )}
              </div>

              <div>
                <label htmlFor="symbol" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Symbol *
                </label>
                <input
                  type="text"
                  id="symbol"
                  value={formData.symbol}
                  onChange={(e) => handleInputChange('symbol', e.target.value)}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.symbol 
                      ? 'border-red-300 dark:border-red-600 bg-red-50 dark:bg-red-900/20' 
                      : 'border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700'
                  } text-slate-900 dark:text-white`}
                  placeholder="e.g., BAYC"
                />
                {errors.symbol && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.symbol}</p>
                )}
              </div>
            </div>

            <div>
              <label htmlFor="contractAddress" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Contract Address *
              </label>
              <input
                type="text"
                id="contractAddress"
                value={formData.contractAddress}
                onChange={(e) => handleInputChange('contractAddress', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.contractAddress 
                    ? 'border-red-300 dark:border-red-600 bg-red-50 dark:bg-red-900/20' 
                    : 'border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700'
                } text-slate-900 dark:text-white`}
                placeholder="0x1234...5678"
              />
              {errors.contractAddress && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.contractAddress}</p>
              )}
            </div>

            <div>
              <label htmlFor="chain" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Blockchain *
              </label>
              <select
                id="chain"
                value={formData.chain}
                onChange={(e) => handleInputChange('chain', e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {chains.map(chain => (
                  <option key={chain} value={chain}>{chain}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Purchase Details */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-slate-900 dark:text-white flex items-center">
              <PoundSterling className="w-5 h-5 mr-2 text-green-600" />
              Purchase Details
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label htmlFor="purchasePrice" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Purchase Price (£) *
                </label>
                <input
                  type="number"
                  id="purchasePrice"
                  value={formData.purchasePrice}
                  onChange={(e) => handleInputChange('purchasePrice', parseFloat(e.target.value) || 0)}
                  step="0.01"
                  min="0"
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.purchasePrice 
                      ? 'border-red-300 dark:border-red-600 bg-red-50 dark:bg-red-900/20' 
                      : 'border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700'
                  } text-slate-900 dark:text-white`}
                  placeholder="0.00"
                />
                {errors.purchasePrice && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.purchasePrice}</p>
                )}
              </div>

              <div>
                <label htmlFor="quantity" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Quantity *
                </label>
                <input
                  type="number"
                  id="quantity"
                  value={formData.quantity}
                  onChange={(e) => handleInputChange('quantity', parseInt(e.target.value) || 0)}
                  min="1"
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.quantity 
                      ? 'border-red-300 dark:border-red-600 bg-red-50 dark:bg-red-900/20' 
                      : 'border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700'
                  } text-slate-900 dark:text-white`}
                  placeholder="1"
                />
                {errors.quantity && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">{errors.quantity}</p>
                )}
              </div>

              <div>
                <label htmlFor="purchaseDate" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Purchase Date *
                </label>
                <input
                  type="date"
                  id="purchaseDate"
                  value={formData.purchaseDate}
                  onChange={(e) => handleInputChange('purchaseDate', e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Additional Notes */}
          <div>
            <label htmlFor="notes" className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Additional Notes
            </label>
            <textarea
              id="notes"
              value={formData.notes}
              onChange={(e) => handleInputChange('notes', e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Any additional information about this asset..."
            />
          </div>

          {/* Form Actions */}
          <div className="flex items-center justify-end space-x-3 pt-4 border-t border-slate-200 dark:border-slate-700">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-slate-700 dark:text-slate-300 bg-slate-100 dark:bg-slate-700 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
            >
              <Plus className="w-4 h-4" />
              <span>Add Asset</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddAssetForm;
