import { IMPLEMENTATION_CONFIG, UI_TEXT } from "../data/index";

const ImplementationDetails = () => {
  return (
    <div className="bg-white p-6 rounded-xl shadow-md mb-8">
      <h2 className="text-xl font-bold text-gray-800 mb-6">
        {UI_TEXT.implementationDetails.title}
      </h2>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0 mt-1">
            <i className="fas fa-external-link-alt text-blue-600"></i>
          </div>
          <div>
            <a
              href={IMPLEMENTATION_CONFIG.sheetUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors duration-200 text-sm font-medium"
            >
              <i className="fas fa-table"></i>
              {IMPLEMENTATION_CONFIG.sheetLinkText}
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImplementationDetails;
