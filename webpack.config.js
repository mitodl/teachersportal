var Promise = require('es6-promise').Promise;
var path = require("path");
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');
var NodeNeat = require("node-neat");

module.exports = {
  context: __dirname,
  entry: {
    'index_page': './static/js/index_page'
  },
  output: {
    path: path.resolve('./static/bundles/'),
    filename: "[name].js"
  },

  module: {
    loaders: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        loader: 'babel-loader',
        query: {
          presets: ['es2015', 'react']
        }
      },  // to transform JSX into JS
      {
        test: /\.scss$/,
        exclude: /node_modules/,
        loader: 'style!css!sass'
      }
    ]
  },

  sassLoader: {
    includePaths: NodeNeat.includePaths
  },

  resolve: {
    modulesDirectories: ['node_modules'],
    extensions: ['', '.js', '.jsx']
  }
};
