import { highlightsData, llmHighlightsData } from "../data/index";

// All titles, descriptions and screenshots come from data/report.json
// (generated from the monthly Word doc). Styling per position matches the original layout.
const HIGHLIGHT_BADGES = [
  "bg-blue-100 text-blue-600",
  "bg-purple-100 text-purple-600",
  "bg-green-100 text-green-600",
  "bg-orange-100 text-orange-600",
];
const LLM_BADGES = [
  "bg-indigo-100 text-indigo-600",
  "bg-emerald-100 text-emerald-600",
  "bg-pink-100 text-pink-600",
];

const HighlightsSection = () => {
  return (
    <div className="mt-10">
      <div className="bg-white rounded-2xl shadow-md p-8 border border-gray-100">
        {/* Header */}
        <div className="mb-10">
          <h2 className="text-3xl font-bold text-gray-900">Highlights</h2>
          <div className="w-20 h-1 bg-blue-600 mt-3 rounded-full"></div>
        </div>

        {highlightsData.map((item, index) => (
          <div className="mb-16" key={index}>
            <div className="flex items-start gap-4 mb-5">
              <div
                className={`w-10 h-10 rounded-full ${HIGHLIGHT_BADGES[index % HIGHLIGHT_BADGES.length]} flex items-center justify-center font-bold text-lg`}
              >
                {index + 1}
              </div>

              <div>
                <h3 className="text-2xl font-semibold text-gray-900 leading-snug">
                  {item.title}
                </h3>

                <p
                  className={`${index === 0 ? "text-gray-600" : "text-gray-700"} mt-4 leading-8 text-[15px] max-w-4xl`}
                >
                  {item.description}
                </p>
              </div>
            </div>

            {item.image && (
              <div className="mt-8 border-2 border-gray-300 rounded-2xl overflow-hidden shadow-md bg-white p-3">
                <img
                  src={item.image}
                  alt={item.title}
                  className="w-full object-cover rounded-lg"
                />
              </div>
            )}
          </div>
        ))}

        {/* LLM Highlights */}
        <div className="mt-20 border-t pt-12">
          <h2 className="text-3xl font-bold text-gray-900">LLM Highlights</h2>
          <div className="w-20 h-1 bg-indigo-600 mt-3 rounded-full mb-10"></div>

          {llmHighlightsData.map((item, index) => (
            <div className={index === 2 ? undefined : "mb-16"} key={index}>
              <div className="flex items-start gap-4 mb-5">
                <div
                  className={`w-10 h-10 rounded-full ${index === 0 ? LLM_BADGES[0] : LLM_BADGES[1 + ((index - 1) % 2)]} flex items-center justify-center font-bold text-lg`}
                >
                  {index + 1}
                </div>

                <div>
                  <h3 className="text-2xl font-semibold text-gray-900">
                    {item.title}
                  </h3>

                  <p className="text-gray-700 mt-4 leading-8 text-[15px] max-w-5xl">
                    {item.description}
                  </p>
                </div>
              </div>

              {item.image && (
                <div className="mt-8 flex justify-center">
                  <div
                    className={`w-full ${index === 0 ? "max-w-4xl" : "max-w-2xl"} border-2 border-gray-300 rounded-2xl overflow-hidden shadow-md bg-white p-4`}
                  >
                    <img
                      src={item.image}
                      alt={item.title}
                      className="w-full h-auto object-contain rounded-lg"
                    />
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default HighlightsSection;
