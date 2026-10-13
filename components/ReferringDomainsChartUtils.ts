export const CHART_CONFIG = {
  scaleDivisions: 4,
  scaleRoundFactor: 10,
  minBarWidthPercent: 2,
  tooltipOffset: { x: 10, y: -40 },
} as const;

export const calculateScaleMax = (maxValue: number): number => {
  return (
    Math.ceil(maxValue / CHART_CONFIG.scaleRoundFactor) *
    CHART_CONFIG.scaleRoundFactor
  );
};

export const generateScalePoints = (scaleMax: number): number[] => {
  const points: number[] = [];
  const step = scaleMax / CHART_CONFIG.scaleDivisions;
  for (let i = 0; i <= CHART_CONFIG.scaleDivisions; i++) {
    points.push(Math.round(i * step));
  }
  return points;
};

export const calculateBarWidth = (value: number, scaleMax: number): number => {
  const width = (value / scaleMax) * 100;
  return Math.max(width, CHART_CONFIG.minBarWidthPercent);
};
