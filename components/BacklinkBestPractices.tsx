import { UI_TEXT } from "../data/index";

const BacklinkBestPractices = () => {
  return (
    <div className="mt-10">
      <div className="bg-white rounded-xl shadow-md p-6">
        <div className="flex items-center mb-6">
          <i className="fa-solid fa-shield-halved text-2xl text-teal-500 mr-3"></i>
          <h2 className="text-2xl font-bold text-gray-800">
            {UI_TEXT.backlinkBestPractices.title}
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="space-y-4">
            <div className="flex items-center mb-3">
              <i className="fa-solid fa-check text-blue-500 mr-2"></i>
              <h3 className="text-lg font-semibold text-blue-600">
                ACQUISITION APPROACH
              </h3>
            </div>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>
                • Backlinks are obtained exclusively through guest posts
                published on relevant, high-quality websites.
              </li>
              <li>
                • No link exchanges, private blog networks (PBNs), or automated
                link-building methods are used.
              </li>
            </ul>
          </div>

          <div className="space-y-4">
            <div className="flex items-center mb-3">
              <i className="fa-solid fa-check text-blue-500 mr-2"></i>
              <h3 className="text-lg font-semibold text-blue-600">
                REFERRING DOMAIN QUALITY
              </h3>
            </div>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>
                • Domains with a Domain Authority (DA) between 30 and 70+ are
                targeted.
              </li>
              <li>
                • Referring domains must demonstrate consistent organic traffic
                of at least 2,000 visits per month on average over the past six
                months
              </li>
              <li>
                • Domains must be topically relevant to the linked website's
                niche, ensuring contextual alignment between the referring page
                and the target page.
              </li>
            </ul>
          </div>

          <div className="space-y-4">
            <div className="flex items-center mb-3">
              <i className="fa-solid fa-check text-blue-500 mr-2"></i>
              <h3 className="text-lg font-semibold text-blue-600">
                ANCHOR TEXT GUIDELINES
              </h3>
            </div>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>
                • No keyword stuffing is permitted. Anchor texts must be
                semantically relevant, natural in phrasing, and contextual to
                the surrounding content.
              </li>
              <li>
                • Anchor texts are typically 4-8 words in length and consist of
                variations or partial matches of the target keyword to maintain
                natural diversity.
              </li>
            </ul>
          </div>

          <div className="space-y-4">
            <div className="flex items-center mb-3">
              <i className="fa-solid fa-check text-blue-500 mr-2"></i>
              <h3 className="text-lg font-semibold text-blue-600">
                CONTENT RELEVANCE & QUALITY
              </h3>
            </div>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>
                • All guest posts must provide unique, valuable, and informative
                content that benefits readers, not solely for link placement.
              </li>
              <li>
                • Content must be topically aligned with both the referring
                site's audience and the target page's subject matter.
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BacklinkBestPractices;
