const GallerySection = () => {
  const photos = [
    {
      url: "https://cdn.poehali.dev/files/photo_2025-12-27_13-32-52.jpg",
      alt: "Красный глиттерный маникюр"
    },
    {
      url: "https://cdn.poehali.dev/files/photo_2025-12-27_13-32-55.jpg",
      alt: "Элегантный красный дизайн ногтей"
    },
    {
      url: "https://cdn.poehali.dev/files/photo_2025-12-27_13-32-49.jpg",
      alt: "Профессиональный маникюр с красным глиттером"
    },
    {
      url: "https://cdn.poehali.dev/files/photo_2025-12-27_13-32-46.jpg",
      alt: "Нежный персиковый маникюр с блестками"
    }
  ];

  return (
    <section id="галерея" className="py-20 px-4 bg-black">
      <div className="container mx-auto">
        <div className="text-center mb-12 animate-fade-in">
          <p className="text-accent text-sm tracking-widest mb-4">НАШИ РАБОТЫ</p>
          <h2 className="text-5xl md:text-6xl font-bold mb-4 text-white">
            Галерея
          </h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            Примеры наших работ — каждый образ создан с любовью и профессионализмом
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {photos.map((photo, index) => (
            <div
              key={index}
              className="group relative overflow-hidden aspect-[3/4] animate-fade-in"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <img
                src={photo.url}
                alt={photo.alt}
                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default GallerySection;
