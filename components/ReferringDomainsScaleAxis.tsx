interface ScaleAxisProps {
  points: number[];
}

const ReferringDomainsScaleAxis = ({ points }: ScaleAxisProps) => (
  <div className="flex justify-between text-xs text-gray-400 ml-24">
    {points.map((point, index) => (
      <span key={index}>{point}</span>
    ))}
  </div>
);

export default ReferringDomainsScaleAxis;
