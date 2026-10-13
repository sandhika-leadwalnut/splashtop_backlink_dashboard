import { REPORT_CONFIG, IMAGE_PATHS } from "../data/index";

const Header = () => {
  return (
    <header className="bg-white shadow-md">
      <div className="container mx-auto px-4 md:px-8 py-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex-shrink-0">
            <img
              src={IMAGE_PATHS.splashtopLogo}
              alt="Splashtop"
              className="h-10 w-auto"
            />
          </div>

          <div className="flex-shrink-0 text-center">
            <img
              src={IMAGE_PATHS.leadwalnutLogo}
              alt="LeadWalnut"
              className="h-10 w-auto mx-auto mb-1"
            />
            <p className="text-xs text-gray-500 font-bold">
              {REPORT_CONFIG.reportDate}
            </p>
          </div>
        </div>

        <div className="text-center">
          <h1 className="text-2xl md:text-3xl font-bold text-gray-800">
            {REPORT_CONFIG.reportTitle}
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            {REPORT_CONFIG.reportSubtitle}
          </p>
        </div>
      </div>
    </header>
  );
};

export default Header;
