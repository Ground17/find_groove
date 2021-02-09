#include <math.h>
#include <stdio.h>


/*
   This computes an in-place complex-to-complex FFT
   x and y are the real and imaginary arrays of 2^m points.
   dir =  1 gives forward transform
   dir = -1 gives reverse transform
*/
short FFT(short int dir, long m, double* x, double* y)
{
    long n, i, i1, j, k, i2, l, l1, l2;
    double c1, c2, tx, ty, t1, t2, u1, u2, z;
    /* Calculate the number of points */
    n = 1;					//initializing n
    for (i = 0; i < m; i++)
        n *= 2;					//n = 2^m
     /* Do the bit reversal */
    i2 = n >> 1;					//n is divided by 2
    j = 0;
    for (i = 0; i < n - 1; i++) {
        if (i < j) {
            tx = x[i];
            ty = y[i];
            x[i] = x[j];
            y[i] = y[j];
            x[j] = tx;
            y[j] = ty;				//exchange the value of x[i] & x[j], y[i] & y[j]
        }
        k = i2;
        while (k <= j) {
            j -= k;
            k >>= 1;
        }
        j += k;
    }
    /* Compute the FFT */
    c1 = -1.0;
    c2 = 0.0;
    l2 = 1;
    for (l = 0; l < m; l++) {
        l1 = l2;
        l2 <<= 1;					//I2 is  multiplied by 2
        u1 = 1.0;
        u2 = 0.0;
        for (j = 0; j < l1; j++) {
            for (i = j; i < n; i += l2) {
                i1 = i + l1;
                t1 = u1 * x[i1] - u2 * y[i1];
                t2 = u1 * y[i1] + u2 * x[i1];
                x[i1] = x[i] - t1;
                y[i1] = y[i] - t2;
                x[i] += t1;
                y[i] += t2;				//butterfly calculation
            }
            z = u1 * c1 - u2 * c2;		//cos(x+y) = cosxcosy - sinxsiny (Real part)
            u2 = u1 * c2 + u2 * c1;		//sin(x+y) = sinxcosy + cosxsiny (Imaginary part)
            u1 = z;
        }
        c2 = sqrt((1.0 - c1) / 2.0);		//sin(x/2) = sqrt((1-cosx)/2)
        if (dir == 1)
            c2 = -c2;
        c1 = sqrt((1.0 + c1) / 2.0);		//cos(x/2) = sqrt((1+cosx)/2)
    }
    /* Scaling for forward transform */
    if (dir == 1) {
        for (i = 0; i < n; i++) {
            x[i] /= n;
            y[i] /= n;				//IFFT formula : scale is divided by n
        }
    }

    return 1;
}

int main()
{
    const int M = 2;
    const int N = 4; // length (= 2 to the M)

    double x['N'] = { 1, 2, 3, 4 }; // real part
    double y['N'] = { 0, 0, 0, 0 }; // imaginary part

    // FFT

    FFT(-1, M, x, y);
    printf("FFT\n");
    for (int i = 0; i < 4; ++i)
    {
        printf("%f + %fi\n", x[i], y[i]);
    }

    // inverse FFT
    FFT(1, M, x, y);

    printf("\nIFFT\n");
    for (int i = 0; i < 4; ++i)
    {
        printf("%f + %fi\n", x[i], y[i]);
    }

    return 0;
}