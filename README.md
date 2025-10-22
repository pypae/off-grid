# ⛷️ off-grid

Demo: [Live App](https://off-grid-app-585848874375.europe-west6.run.app/)

---

`off-grid` is an experimental project aimed at automating ski tour generation using A\* search on categorical avalanche terrain maps. This project is primarily a learning exercise for working with geospatial data, inspired largely by [information available on Skitourenguru (German)](https://info.skitourenguru.ch/index.php/corridors). For a production-grade tool, please use the beta feautre on [Skitourenguru](https://www.skitourenguru.ch/rating-view).

The A\* pathfinding algorithm was implemented based on [this insightful blog post by Red Blob Games](https://www.redblobgames.com/pathfinding/a-star/introduction.html), and avalanche terrain data was sourced from the [SLF Categorical Avalanche Terrain Maps](https://content.whiterisk.ch/en/help/maps/classified-avalanche-terrain-cat).

---

## Table of Contents

- [🛠 Development](#-development)
  - [Prerequisites](#prerequisites)
  - [Backend](#backend)
  - [Frontend](#frontend)
- [🚀 Deployment](#-deployment)
- [📐 How it Works](#-how-it-works)
- [📜 License](#-license)

## 🛠 Development

This project has both backend and frontend components. It requires a Python environment for backend processes and a Node.js/Next.js environment for the frontend.

<details>
<summary>Click to view project structure</summary>

```plaintext
├── api.Dockerfile                   # Dockerfile for the FastAPI backend service
├── app.Dockerfile                   # Dockerfile for the Next.js frontend service
├── pyproject.toml                   # Python dependencies and project configuration for the backend
├── package.json                     # Dependencies and scripts for the frontend
├── ...
├── data/                            # Directory containing input data for terrain analysis
│   ├── ncat-10.tif                  # Main avalanche terrain categorization dataset
│   └── ...
├── scripts/                         # Helper scripts for data handling and preparation
│   ├── convert_cat.py               # Converts avalanche data from rgba- to categorical (0-10) values
│   ├── download_slf_layers.py       # Downloads SLF categorical avalanche terrain data
│   └── ...
├── src/                             # Source code for backend and frontend
│   ├── app/                         # Frontend application files
│   │   ├── components/              # Reusable components, like the map display
│   │   ├── layout.tsx               # Layout structure for the app
│   │   └── page.tsx                 # Main page component for rendering content
│   └── off_grid/                    # Backend application files
│       ├── main.py                  # FastAPI server setup and route definitions
│       ├── pathfinding.py           # Core A* pathfinding logic and algorithms
│       ├── util.py                  # Utility functions supporting pathfinding and data processing
```

</details>

### Prerequisites

- **hatch**: Used for managing Python environments. [Installation Guide](https://hatch.pypa.io/latest/install/).
- **npm**: Used for managing Node.js environments. [Installation Guide](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm).

### Backend

1. **Download Data**  
   Download the categorical avalanche terrain data to the `./data` directory. For example:

   ```bash
   wget -P ./data https://storage.googleapis.com/off-grid-440012.appspot.com/data/ncat-10.tif
   ```

   ```bash
   wget -P ./data https://storage.googleapis.com/off-grid-440012.appspot.com/data/ ski_routes_mask.tif 
   ```

   > **Note**: More information on the dataset can be found in the [How it works](#how-it-works) section.

2. **Install GDAL**  
   GDAL is a geospatial data library necessary for handling the terrain data. Install using your package manager (e.g., Homebrew):

   ```bash
   brew install gdal
   ```

3. **Run Development Server**  
   Start the FastAPI development server:

   ```shell
   hatch run fastapi dev src/off_grid/main.py
   ```

   This command sets up a hatch environment, installs dependencies, and runs the server in development mode. Once started, API documentation is available at `http://localhost:8000/docs`. Any changes to Python files will be automatically applied.

### Frontend

1. **Install Dependencies**

   ```shell
   npm install
   ```

2. **Run Development Server with Hot Reloading**

   ```shell
   npm run dev
   ```

   Visit the app at `http://localhost:3000` to view the frontend. Any changes made to frontend files will trigger hot reloading, so updates appear immediately without a full page refresh.

## 🚀 Deployment

Both the API and frontend are containerized and deployed on GCP Cloud Run. The services are built from Docker files using **GCP Cloud Build**, which automatically triggers builds and deployments on pushes to the `main` branch. Here’s a breakdown of how it works:

- **Docker Compose**: The `docker-compose.yml` defines both API and frontend services for consistent builds locally and in production.
  - `api.Dockerfile`: Builds the FastAPI backend service.
  - `app.Dockerfile`: Builds the Next.js frontend service.
- **GCP Cloud Build**: GCP automatically builds each Docker image, creates containers, and deploys them to Cloud Run.
- **URLs**:
  - **Frontend App**: Accessible at [off-grid-app](https://off-grid-app-585848874375.europe-west6.run.app/)
  - **API Endpoint**: Available at [shortest-path endpoint](https://off-grid-585848874375.europe-west6.run.app/shortest-path)

## 📐 How it Works

The `off-grid` tool generates ski tours by calculating the shortest safe path across categorized avalanche terrain. It uses:

- **A\* Search Algorithm**: A popular pathfinding algorithm, working well on raster data.
- **Categorical Avalanche Terrain Maps**: These maps divide terrain into categories based on avalanche risk, allowing the tool to avoid high-risk areas. This data is provided by the [Swiss Institute for Snow and Avalanche Research (SLF)](https://www.slf.ch/en/).

// Todo

## 📜 License

`off-grid` is distributed under the terms of the [MIT License](https://spdx.org/licenses/MIT.html).
