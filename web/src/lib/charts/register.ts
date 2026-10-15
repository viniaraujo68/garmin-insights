import {
  BarController,
  BarElement,
  CategoryScale,
  Chart,
  Filler,
  Legend,
  LinearScale,
  LineController,
  LineElement,
  PointElement,
  ScatterController,
  Tooltip,
} from "chart.js";

let registered = false;

export const registerCharts = (): void => {
  if (registered) return;
  Chart.register(
    LineController,
    BarController,
    ScatterController,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    Filler,
    Tooltip,
    Legend,
  );
  registered = true;
};
