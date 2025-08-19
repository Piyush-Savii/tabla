# 🧠 Virtual Assistant API

A cross-platform virtual assistant built using **FastAPI**, supporting integration with Slack, Telegram, Discord, and MS Teams. The assistant routes user messages to powerful LLMs such as **OpenAI GPT** and **Google Gemini** for smart responses.

---

## 🚀 Features

- 🔌 Pluggable LLM support (OpenAI, Google Gemini, etc.)
- 💬 Chatbot integration with:
  - Slack
  - Telegram
  - Discord
  - Microsoft Teams
- ⚙️ YAML-based provider configuration
- 🛠️ Environment-based setup (.env)
- 🔍 Optional performance profiling
- 🧾 Smart dependency management using `packaging` and `importlib.metadata`
- 🧪 LLM connection testing at runtime
- 📦 Modular codebase for LLM, platform, and logging

---

# 🏗️ Virtual Assistant Platform — Architecture Overview

## 🎯 Purpose

This assistant is designed to help users interact with business data using natural language. It supports querying databases and generating visualizations using an LLM (e.g., OpenAI) backed by a modular Python server.

---

## 🧱 Core Components

### 1. **FastAPI Server (`main.py`)**

* Hosts the API and exposes endpoints
* Mounts platform-specific routers (Slack, etc.)
* Configures logging, profiling, and CORS

### 2. **Platform Router (`platform.py`)**

* Handles incoming events (e.g., Slack `/events`)
* Extracts user ID, message, and channel
* Passes enriched context to the LLM

### 3. **User Session Manager (`user_manager.py`)**

* Tracks users and stores per-user message history
* Prevents duplicate event processing

### 4. **LLM Client (`llm_client.py`)**

* Sends messages to the LLM (OpenAI/Gemini)
* Interprets responses and handles tool/function calls

### 5. **Function Dispatcher (`router.py`)**

* Maps LLM tool names to Python functions
* Executes data queries and visualizations
* Returns structured results for LLM continuation

### 6. **Tools Layer (`tool/`)**

* `googledb`: Runs BigQuery queries
* `visualization.wrappers`: Plots charts based on AI inputs

---

## 🔁 Workflow Summary

1. A user mentions the bot in Slack.
2. Slack forwards the event to `/slack/events`.
3. `platform.py` validates and extracts the query.
4. The message + history + prompt is sent to `llm_client`.
5. The LLM responds:

   * Directly (text response)
   * Or via tool\_call (e.g., "create\_bar\_chart")
6. If a tool is called:

   * `router.py` executes it and returns a result
   * LLM is invoked again with the new data
7. The assistant’s response is posted back to Slack.

---

## 🧠 LLM Use

* OpenAI models like `gpt-4-0613`
* Receives `system`, `user`, and `assistant` messages
* Can invoke tools via function-calling API

---

## 🛠️ Extensibility

* Add platforms by extending `PlatformBase`
* Add tools by updating `FUNCTION_REGISTRY`
* Add endpoints by modifying FastAPI routers

---

## ✅ Status

* Designed for modularity
* Local + cloud deployable
* Easily testable with mock Slack or REST requests


## 📁 Project Structure

# 📘 Function Registry Documentation

This document lists all available functions that the virtual assistant can call via tool use, grouped by category.

---

## 🗃️ Categories

### 📂 Database Functions

| Function Name       | Description                                                              |
|---------------------|--------------------------------------------------------------------------|
| `execute_sql_query` | Executes a SQL query and returns the result from the connected database. |

### 📊 Visualization Functions

| Function Name                          | Description                                       |
|----------------------------------------|---------------------------------------------------|
| `create_bar_chart`                     | Generates a bar chart from provided data.         |
| `create_pie_chart`                     | Creates a pie chart visualizing categorical data. |
| `create_single_line_graph`             | Draws a line chart for a single time series.      |
| `create_multiple_line_graph`           | Draws a line chart comparing multiple series.     |
| `create_single_area_chart`             | Builds an area chart for one data series.         |
| `create_stacked_area_chart`            | Builds a stacked area chart for multiple series.  |
| `create_single_product_radar_chart`    | Plots radar chart for one product/variable.       |
| `create_multiple_products_radar_chart` | Compares multiple products in a radar chart.      |
| `create_scatter_plot`                  | Displays two-dimensional correlation.             |
| `create_heatmap`                       | Plots a heatmap for matrix-style data.            |
| `create_bubble_chart`                  | Shows multi-dimensional data in a bubble chart.   |
| `create_waterfall_chart`               | Visualizes cumulative impact with waterfall view. |
| `create_funnel_chart`                  | Plots conversion steps in a funnel layout.        |

---

## 🔄 How it works

Each function is triggered by the LLM (like OpenAI) when the assistant determines a tool is needed. The platform routes the request to the corresponding Python function and returns the result.

The function response is then interpreted or directly presented back to the user, often with additional context from the LLM.


# 🧩 Function Registry Configuration (YAML-style reference)

## database:

* name: execute\_sql\_query
  description: Executes a SQL query and returns the results
  parameters:

  * query: SQL string to be executed

## visualization:

* name: create\_bar\_chart
  description: Generates a bar chart from structured input
  parameters:

  * data: Structured dataset or dictionary
  * x\_axis: Field for x-axis
  * y\_axis: Field for y-axis

* name: create\_pie\_chart
  description: Creates a pie chart for categorical data
  parameters:

  * labels: List of category names
  * values: List of numeric values

* name: create\_single\_line\_graph
  description: Plots a single time-series line graph
  parameters:

  * data: Dataset
  * x: X-axis field
  * y: Y-axis field

* name: create\_multiple\_line\_graph
  description: Compares multiple series in one chart
  parameters:

  * data: Dataset
  * series: List of series to plot

* name: create\_single\_area\_chart
  description: Plots a filled area chart for one series
  parameters:

  * data: Dataset
  * x: Field for x-axis
  * y: Field for y-axis

* name: create\_stacked\_area\_chart
  description: Visualizes stacked values over time
  parameters:

  * data: Dataset
  * groups: Field to group stacked areas by

* name: create\_single\_product\_radar\_chart
  description: Plots characteristics of a single product
  parameters:

  * metrics: Key metrics dictionary

* name: create\_multiple\_products\_radar\_chart
  description: Compares products on multiple metrics
  parameters:

  * products: Dictionary of product names and metric sets

* name: create\_scatter\_plot
  description: Shows correlations in data via scatter points
  parameters:

  * x\_values: List of values for x-axis
  * y\_values: List of values for y-axis

* name: create\_heatmap
  description: Plots a heatmap for a 2D matrix
  parameters:

  * matrix: 2D list or numpy matrix

* name: create\_bubble\_chart
  description: Visualizes multi-dimensional data with bubble size
  parameters:

  * x: X-axis data
  * y: Y-axis data
  * size: Bubble size values

* name: create\_waterfall\_chart
  description: Visualizes step-by-step composition of value
  parameters:

  * steps: List of step labels and values

* name: create\_funnel\_chart
  description: Displays conversion steps in a funnel layout
  parameters:

  * steps: List of funnel stages with counts

