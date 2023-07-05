function mean_data = mean_fmridata(runfile, outputfile)

    image = fmri_data(runfile); 
    mean_data = mean(image); 
    
    write(mean_data, 'fname', outputfile);

end