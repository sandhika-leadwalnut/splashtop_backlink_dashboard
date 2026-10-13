import { KEY_FINDINGS } from "../data/index";

// Renders **bold** segments inside a finding's description, so emphasis can be
// authored directly in the data file (mirrors the Word doc formatting).
const renderWithEmphasis = (text: string) =>
  text.split(/(\*\*[^*]+\*\*)/g).map((part, i) =>
    part.startsWith("**") && part.endsWith("**") ? (
      <strong key={i} className="font-semibold text-gray-900">
        {part.slice(2, -2)}
      </strong>
    ) : (
      part
    )
  );

const KeyFindings = () => {
  const findings = KEY_FINDINGS;

  return (
    <div className="bg-white p-6 rounded-xl shadow-md mb-8">
      <h2 className="text-xl font-bold text-gray-800 mb-4">Key Findings</h2>

      <ul className="divide-y divide-gray-100">
        {findings.map((finding, index) => (
          <li key={index} className="flex items-start gap-3 py-3">
            <i
              className={`${finding.icon} ${finding.color} text-base mt-1 flex-shrink-0`}
            ></i>
            <p className="text-sm text-gray-600 leading-relaxed">
              {renderWithEmphasis(finding.description)}
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default KeyFindings;
