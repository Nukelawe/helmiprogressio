gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.5 \
   -dBATCH -dNOPAUSE -dQUIET \
   -sOutputFile=output/helmiprogressio.pdf \
   -c "[ /Title (Sinkkunarun tasoj\344rjestelm\344) /Author (Matias Ruotsalainen) /DOCINFO pdfmark" \
   -f output/helmiprogressio_nometa.pdf
